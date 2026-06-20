"""
finance_a2a.py
==============
The same Finance scenario, now as a multi-agent system:

  UserRequest
      └─> TradeOrchestrator
              ├─> ResearchAgent   (read_market only)
              ├─> ExecutionAgent  (execute_trade, with $10k ceiling)
              └─> ComplianceAgent (append_ledger only, append-only)

This file demonstrates three A2A attack patterns and why scoped
architecture defeats all three without extra governance gates:

  ATTACK 1 — Token-scope escalation:
    A compromised upstream caller widens its delegation token to include
    capabilities it was never granted. Blocked: the orchestrator's
    delegation-rights registry doesn't recognise the capability.

  ATTACK 2 — Lateral agent call (peer-to-peer injection):
    A compromised ResearchAgent tries to call ExecutionAgent directly,
    bypassing the orchestrator entirely. Blocked: subagents have no
    peer-call interface — they only surface tool boundaries.

  ATTACK 3 — Orchestrator compromise + delegation widening:
    A compromised orchestrator tries to delegate a capability to a subagent
    that was never registered as delegatable to it. Blocked: the
    DelegationToken narrows at each hop and cannot widen.

Run it:  python finance_a2a.py  (stdlib only, no API keys)
"""

from __future__ import annotations

from agent_harness import (
    Agent, DelegationToken, Orchestrator, Tool, attempt
)

TRANSFER_CEILING = 10_000
LEDGER: list[str] = []
BALANCE = {"house": 1_000_000}


# --- tool bodies -----------------------------------------------------------
def read_market(symbol: str = "") -> str:
    return f"{symbol} = $100.00"


def execute_trade(symbol: str = "", amount_usd: float = 0.0, to: str = "") -> str:
    BALANCE["house"] -= amount_usd
    return f"transferred ${amount_usd:,.2f} to {to!r}; house ${BALANCE['house']:,.2f}"


def under_ceiling(symbol: str = "", amount_usd: float = 0.0, to: str = "") -> bool:
    return 0 < amount_usd <= TRANSFER_CEILING


def append_ledger(entry: str = "") -> str:
    LEDGER.append(entry)
    return f"ledger now has {len(LEDGER)} entries (append-only)"


# --- build agents + orchestrator -------------------------------------------
def build_fleet() -> Orchestrator:
    research = Agent("ResearchAgent")
    research.grant(Tool("read_market", run=read_market))

    execution = Agent("ExecutionAgent")
    execution.grant(Tool("execute_trade", run=execute_trade, guard=under_ceiling))

    compliance = Agent("ComplianceAgent")
    compliance.grant(Tool("append_ledger", run=append_ledger))

    orch = Orchestrator("TradeOrchestrator")
    orch.register(research,   delegatable=["read_market"])
    orch.register(execution,  delegatable=["execute_trade"])
    orch.register(compliance, delegatable=["append_ledger"])
    return orch


def main() -> None:
    orch = build_fleet()
    print("=== FINANCE A2A: scoped multi-agent fleet ===\n")

    # --- Normal multi-hop flow -------------------------------------------
    print("--- Normal flow: user request → orchestrator → subagents ---\n")
    user_token = DelegationToken(
        issuer="UserRequest",
        scope=["read_market", "execute_trade", "append_ledger"],
    )
    print(orch.delegate(user_token, "ResearchAgent",   "read_market",    symbol="ACME"))
    print(orch.delegate(user_token, "ExecutionAgent",  "execute_trade",  symbol="ACME", amount_usd=5_000, to="broker"))
    print(orch.delegate(user_token, "ComplianceAgent", "append_ledger",  entry="trade ACME $5,000 to broker"))

    # --- ATTACK 1: Token-scope escalation --------------------------------
    print("\n--- ATTACK 1: token-scope escalation ---\n")
    # Attacker widens the token to include erase_ledger, which does not
    # exist anywhere in the fleet.
    evil_token = DelegationToken(
        issuer="CompromisedUpstream",
        scope=["read_market", "execute_trade", "append_ledger", "erase_ledger"],
    )
    print(orch.delegate(evil_token, "ComplianceAgent", "erase_ledger", entry_contains="attacker"))
    # Blocked: orchestrator's delegation_rights for ComplianceAgent
    # only lists append_ledger — erase_ledger is not registered.

    # --- ATTACK 2: Lateral peer-to-peer call -----------------------------
    print("\n--- ATTACK 2: compromised ResearchAgent tries to call ExecutionAgent directly ---\n")
    # Subagents expose only their own tool boundary.
    # ResearchAgent has no execute_trade capability — it cannot reach the
    # ExecutionAgent at all, because agents don't have peer-call methods.
    research_agent = orch.subagents["ResearchAgent"]
    print(attempt(research_agent, "execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet"))
    # DENIED (scope): ResearchAgent only has read_market.

    # --- ATTACK 3: Orchestrator compromise + delegation widening ---------
    print("\n--- ATTACK 3: compromised orchestrator tries to widen delegation ---\n")
    # Even if the orchestrator is compromised, it cannot delegate a
    # capability to a subagent that the subagent was not registered with.
    # The subagent's own tool boundary is the last line of defence.
    print(orch.delegate(user_token, "ExecutionAgent", "erase_ledger", entry_contains="attacker"))
    # DENIED (delegation): orchestrator has no right to delegate erase_ledger.

    # Also: orchestrator cannot widen a narrowed token —
    # DelegationToken.delegate() enforces monotonic scope reduction.
    narrow_token = DelegationToken(issuer="UserRequest", scope=["read_market"])
    try:
        # Attempt to widen read_market token to include execute_trade:
        widened = narrow_token.delegate("TradeOrchestrator", ["read_market", "execute_trade"])
        print(f"WIDENED (should never print): {widened}")
    except Exception as exc:
        print(f"DENIED  (token-widen)  {exc}")

    print(f"\nFinal ledger: {LEDGER}")
    print("\nResult: all three A2A attack patterns blocked by architecture,")
    print("not by a downstream policy engine. The scope boundary is the gate.")


if __name__ == "__main__":
    main()
