"""
test_finance_kit.py
===================
Stress test for all finance examples before any code goes public.
Tests edge cases, boundary conditions, and adversarial inputs
the happy-path demos don't cover.

Run:  python test_finance_kit.py
"""

from __future__ import annotations
import sys
import traceback
from agent_harness import Agent, DelegationToken, Orchestrator, Tool, attempt, CapabilityDenied, GuardDenied

PASS = 0
FAIL = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global PASS, FAIL
    if condition:
        print(f"  PASS  {label}")
        PASS += 1
    else:
        print(f"  FAIL  {label}" + (f" — {detail}" if detail else ""))
        FAIL += 1


def section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


# ===========================================================================
# 1. Harness primitives
# ===========================================================================
section("1. Harness primitives")

# Basic allow
echo = Tool("echo", run=lambda msg="": f"echo:{msg}")
a = Agent("A")
a.grant(echo)
result = attempt(a, "echo", msg="hi")
check("Basic tool call allowed", "ALLOWED" in result)

# Scope denial
result = attempt(a, "nonexistent")
check("Unknown capability denied (scope)", "DENIED" in result and "scope" in result)

# Guard denial
guarded = Tool("guarded", run=lambda x=0: f"ok:{x}", guard=lambda x=0: x < 100)
b = Agent("B")
b.grant(guarded)
result = attempt(b, "guarded", x=50)
check("Guard allows when condition met", "ALLOWED" in result)
result = attempt(b, "guarded", x=200)
check("Guard denies when condition exceeded", "DENIED" in result and "guard" in result)

# Empty agent
empty = Agent("Empty")
result = attempt(empty, "anything")
check("Empty agent denies everything", "DENIED" in result)

# Tool name with spaces/special chars
weird = Tool("my-tool.v2", run=lambda: "ok")
c = Agent("C")
c.grant(weird)
result = attempt(c, "my-tool.v2")
check("Tool names with hyphens/dots work", "ALLOWED" in result)

# ===========================================================================
# 2. DelegationToken — boundary conditions
# ===========================================================================
section("2. DelegationToken boundary conditions")

# Normal narrowing
t1 = DelegationToken(issuer="Root", scope=["a", "b", "c"])
t2 = t1.delegate("Child", ["a", "b"])
check("Delegation narrows scope correctly", t2.scope == ["a", "b"])
check("Hop chain recorded", "Root" in t2.hops)

# Widening attempt raises
try:
    t3 = t1.delegate("Evil", ["a", "b", "c", "d"])
    check("Widening delegation blocked", False, "should have raised")
except CapabilityDenied as e:
    check("Widening delegation blocked", True)

# Delegate to same scope (equal, not wider — should be allowed)
t4 = t1.delegate("Same", ["a", "b", "c"])
check("Delegation to same scope allowed", t4.scope == ["a", "b", "c"])

# Empty scope delegation
t5 = t1.delegate("Empty", [])
check("Delegation to empty scope allowed", t5.scope == [])

# Deep chain
tok = DelegationToken(issuer="Level0", scope=["x"])
for i in range(1, 10):
    tok = tok.delegate(f"Level{i}", ["x"])
check("Deep delegation chain (9 hops) works", len(tok.hops) == 9)
check("Deep chain scope preserved", tok.scope == ["x"])

# ===========================================================================
# 3. Orchestrator routing
# ===========================================================================
section("3. Orchestrator routing")

# Setup
LEDGER = []
BALANCE = {"h": 1_000_000}
CEILING = 10_000

res_agent = Agent("Res")
res_agent.grant(Tool("read_market", run=lambda symbol="": f"{symbol}=$100"))

exec_agent = Agent("Exec")
exec_agent.grant(Tool("execute_trade",
    run=lambda symbol="", amount_usd=0.0, to="": (
        BALANCE.__setitem__("h", BALANCE["h"] - amount_usd) or
        f"transferred ${amount_usd:,.0f} to {to}"
    ),
    guard=lambda symbol="", amount_usd=0.0, to="": 0 < amount_usd <= CEILING
))

comp_agent = Agent("Comp")
comp_agent.grant(Tool("append_ledger",
    run=lambda entry="": (LEDGER.append(entry) or f"ledger:{len(LEDGER)}")
))

orch = Orchestrator("Orch")
orch.register(res_agent,  delegatable=["read_market"])
orch.register(exec_agent, delegatable=["execute_trade"])
orch.register(comp_agent, delegatable=["append_ledger"])

user_tok = DelegationToken(issuer="User", scope=["read_market", "execute_trade", "append_ledger"])

# Normal routing works
r = orch.delegate(user_tok, "Res", "read_market", symbol="ACME")
check("Orchestrator routes to ResearchAgent", "ALLOWED" in r)

# Unregistered agent
r = orch.delegate(user_tok, "GhostAgent", "read_market")
check("Unregistered agent denied (routing)", "DENIED" in r and "routing" in r)

# Capability not in delegation_rights for that agent
r = orch.delegate(user_tok, "Res", "execute_trade", symbol="X", amount_usd=100, to="y")
check("Capability not in delegation_rights denied", "DENIED" in r and "delegation" in r)

# Capability not in token scope
narrow_tok = DelegationToken(issuer="User", scope=["read_market"])
r = orch.delegate(narrow_tok, "Exec", "execute_trade", symbol="X", amount_usd=100, to="y")
check("Capability not in token scope denied", "DENIED" in r and "token-scope" in r)

# Guard still fires through orchestrator
big_tok = DelegationToken(issuer="User", scope=["execute_trade"])
r = orch.delegate(big_tok, "Exec", "execute_trade", symbol="X", amount_usd=999_999, to="bad")
check("Guard fires through orchestrator (oversized trade)", "DENIED" in r and "boundary" in r)

# Legitimate trade at ceiling boundary
r = orch.delegate(big_tok, "Exec", "execute_trade", symbol="X", amount_usd=CEILING, to="broker")
check("Trade exactly at ceiling allowed", "ALLOWED" in r)

r = orch.delegate(big_tok, "Exec", "execute_trade", symbol="X", amount_usd=CEILING + 0.01, to="broker")
check("Trade 1 cent over ceiling denied", "DENIED" in r)

# ===========================================================================
# 4. A2A attack patterns
# ===========================================================================
section("4. A2A attack patterns")

# Peer-to-peer lateral call — ResearchAgent tries to call exec_trade directly
r = attempt(res_agent, "execute_trade", symbol="X", amount_usd=950_000, to="attacker")
check("Lateral peer-to-peer call denied at scope boundary", "DENIED" in r and "scope" in r)

# Token widening at orchestrator level
narrow = DelegationToken(issuer="User", scope=["read_market"])
try:
    widened = narrow.delegate("Orch", ["read_market", "execute_trade"])
    check("Token widening at orchestrator blocked", False, "should have raised")
except CapabilityDenied:
    check("Token widening at orchestrator blocked", True)

# Capability injection via unknown agent name
r = orch.delegate(user_tok, "../../../etc/passwd", "read_market")
check("Path-traversal agent name handled", "DENIED" in r)

r = orch.delegate(user_tok, "", "read_market")
check("Empty agent name handled", "DENIED" in r)

# ===========================================================================
# 5. Edge cases: types and values
# ===========================================================================
section("5. Edge cases — types and values")

# Zero amount — guard rejects (0 is not a valid trade amount)
r = orch.delegate(big_tok, "Exec", "execute_trade", symbol="X", amount_usd=0.0, to="broker")
check("Zero-amount trade rejected by guard", "DENIED" in r)

# Negative amount — guard now correctly rejects it
r = orch.delegate(big_tok, "Exec", "execute_trade", symbol="X", amount_usd=-500, to="broker")
check("Negative amount rejected by guard", "DENIED" in r)

# Empty string capability
r = attempt(res_agent, "")
check("Empty string capability denied", "DENIED" in r)

# Very long capability name
r = attempt(res_agent, "a" * 1000)
check("Very long capability name denied cleanly", "DENIED" in r)

# ===========================================================================
# Summary
# ===========================================================================
print(f"\n{'='*60}")
print(f"  Results: {PASS} passed, {FAIL} failed")
if FAIL > 0:
    print("  ISSUES TO FIX BEFORE PUBLISH:")
print('='*60)
