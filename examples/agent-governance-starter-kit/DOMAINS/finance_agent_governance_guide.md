# Hardening Financial AI Agents, Part 2: The Architecture Comes Before the Gate

*Why the most expensive policy you'll ever write is the one a well-scoped agent makes unnecessary.*

---

In *Hardening Financial AI Agents: A Deterministic Pulse for 2026*, I argued that "safety" in financial AI is too often a probabilistic suggestion — we ask an LLM to *be careful* with a transfer and hope the system prompt holds.

Here's how well that holds. Take a typical, well-meaning finance system prompt:

> *You are a helpful financial operations assistant. You can read market data, execute trades, and update the compliance ledger. Always be careful with large transfers and follow company policy.*

Run it through Microsoft's Agent Governance Toolkit (`pip install agent-governance-toolkit`), whose `PromptDefenseEvaluator` statically scores a prompt against 12 known injection vectors:

```
Grade:  F
Score:  8 / 100
Undefended attack vectors: 11 of 12
```

Eleven of twelve vectors undefended — instruction-override, indirect-injection, social-engineering, the works. That's not a number I'm asking you to trust; it's deterministic, and the script (`prompt_defense_baseline.py`) is in the kit. Run it, get the same grade.

That post was about the gate you add *after* the prompt fails. This one is about what sits **underneath** the gate — the part most teams skip straight past.

The uncomfortable pattern I keep seeing on red-team engagements: **most of the deterministic gates a financial agent system needs only exist because the architecture handed one agent powers it should never have held at the same time.** Tighten the architecture first, and a large share of your policy surface evaporates. You write fewer gates, and the ones that remain are the ones that matter.

Let me show you, with code you can run.

---

## A note on what these examples model

The examples below are **architecture demonstrations, not a runtime**. They model the part that matters for this argument — *which actor holds which capability, and what crosses between actors* — using plain Python objects. There is no live LLM and no prompt parsing in the demo code; when I say "a prompt-injected instruction arrives," I mean the agent has been induced to attempt an action, and the question on the table is purely: *can the architecture let that action through?* That's the layer this post is about. Prompt-level defenses (the AGT score above) are a separate, complementary layer.

**Threat model for the examples:** the LLM driving any given agent is assumed already compromised — an attacker can make it attempt any action that agent is *capable* of. We are not trying to stop the model from being tricked. We are making sure that when it is tricked, the blast radius is bounded by what that single agent was scoped to do. Out of scope: the security of the underlying tool credentials themselves (see the caveat on shared credentials below) and the signing of delegation tokens (noted where it matters).

---

## The anti-pattern: one agent, every key on the ring

Walk into almost any "AI-powered finance ops" prototype and you'll find a single, helpful, catastrophically over-privileged agent. It can read the market. It can execute trades. It can write to the compliance ledger. Often — because someone wired up a generic database tool — it can *edit* that ledger too.

Nobody designed it to be dangerous. It accreted, one convenient tool per sprint.

Watch what one injected instruction does:

```python
# finance_bad_architecture.py  (stdlib only, no API keys)
agent = build_monolithic_agent()   # one agent, all four capabilities

# ...an injected instruction induces the agent to:
agent.call("execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet")
agent.call("write_ledger", entry="trade ACME $950,000 to attacker-wallet")
agent.call("erase_ledger", entry_contains="attacker-wallet")
```

Output:

```
ALLOWED  execute_trade(amount_usd=950000, to='attacker-wallet') :: transferred $950,000.00
ALLOWED  write_ledger(...) :: ledger now has 2 entries
ALLOWED  erase_ledger(entry_contains='attacker-wallet') :: erased 1 ledger entries
Final ledger entries: ['trade ACME $5,000 to broker']  <- the theft entry is gone
```

A near-million-dollar transfer, logged, then the log scrubbed — by one actor. **No individual gate failed.** There was no buggy policy to point at. The architecture failed: one actor could both move unbounded money and rewrite the record of having done it.

This is where teams reach for more middleware — a transfer-approval gate, an immutable-ledger policy, an anomaly detector. All real controls. But notice what's happening: you're spending deterministic governance to *re-impose boundaries the architecture dissolved.*

---

## The fix: scope first, gate second

Give the same three jobs to three agents that can only do their own job:

- **ResearchAgent** can *only* read the market. No money, no ledger.
- **ExecutionAgent** can execute trades, bounded by a per-trade ceiling guard. It cannot touch the ledger.
- **ComplianceAgent** can *append* to the ledger. It is not granted any erase capability — and neither is any other agent.

```python
# finance_good_architecture.py — the SAME attack, attempted:
execution.call("execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet")
execution.call("erase_ledger", entry_contains="attacker-wallet")
compliance.call("erase_ledger", entry_contains="attacker-wallet")
```

Output:

```
DENIED (guard)  execute_trade ... 950000 exceeds the 10,000 ceiling
DENIED (scope)  'ExecutionAgent' has no capability 'erase_ledger'
DENIED (scope)  'ComplianceAgent' has no capability 'erase_ledger'
```

The oversized transfer is refused at the capability boundary. And the erase isn't *blocked by a policy* — no agent was *granted* that capability, so there's no policy to evaluate, nothing to misconfigure, nothing to forget to enable.

**One honest caveat, because it's the thing a sharp reviewer will raise:** "no agent is granted erase" is an architectural guarantee about the *capability layer*, not a magic one. If your ComplianceAgent's append capability is implemented over a database credential that also permits `DELETE`, then erasure is still reachable through that credential — the scoping moved the problem, it didn't vaporize it. Capability scoping has to be enforced all the way down to the credential the tool actually holds (an append-only ledger table, a write-only API scope). Scope the capability *and* the credential, and the attack is genuinely gone. Scope only the capability and you've made it much harder but not impossible. Say which one you've done.

---

## Why this is the cheaper system, not just the safer one

I'm not walking back deterministic governance — don't trust the model, enforce the boundary. I'm saying the boundary belongs in the **capability grant** before it belongs in a policy engine.

What each design costs you in gates:

| Threat | Monolithic agent needs… | Scoped agents need… |
|---|---|---|
| Oversized transfer | a transfer-amount approval policy | one ceiling guard on the trade capability |
| Audit-trail tampering | an immutable-ledger policy + tamper detection | no erase capability granted (+ append-only credential) |
| Trade by the wrong component | role checks on every tool call | nothing — research agent has no trade tool |
| Privilege bleed across tasks | per-request scope enforcement | nothing — scope is per-agent, structurally |

Three of four rows shrink to "nothing" or "one credential setting." The survivor — the transfer ceiling — is a single legible guard living next to the capability it bounds, where an auditor can find it.

**Fewer gates isn't a convenience; in a regulated environment it's a control objective.** Every policy you maintain can rot, drift, or be silently disabled. The least-risky gate is the one you never had to write.

(One more reviewer-bait detail worth getting right: a ceiling guard should reject `amount <= 0` too. A `$0` or negative "trade" is exactly the kind of edge case an attacker probes. The guard in the kit is `0 < amount_usd <= CEILING`, not just `<= CEILING` — bound the whole valid range, not one end of it.)

---

## When agents talk to agents: the A2A surface

Single-agent scoping is the foundation. Real systems are fleets: an orchestrator coordinates research, execution, and compliance subagents, each of which may delegate further. Every hop is attack surface.

Three A2A patterns, and how scoped architecture answers each. **Important caveat up front:** the delegation token in these examples is a plain object, not a signed credential. The "can't widen the token" guarantee below holds *only* if the token is tamper-evident — a signed JWT or SPIFFE SVID in a real system. An unsigned token can simply be reconstructed by a compromised hop. Treat the code as modeling the *logic* of scoped delegation; the cryptographic binding is assumed, and called out here because pretending otherwise is how these systems actually get broken.

**Attack 1 — Token-scope escalation.** A compromised upstream caller presents a token claiming capabilities it was never granted. The orchestrator's delegation-rights registry doesn't recognise the capability for that agent, so the call dies before reaching a subagent.

**Attack 2 — Lateral peer call.** A compromised ResearchAgent tries to act as the ExecutionAgent. In this architecture there is no peer channel: subagents are reachable only through the orchestrator, and ResearchAgent's own capability set contains only `read_market`. The attempt to invoke `execute_trade` is refused at ResearchAgent's scope boundary — it has no such capability to call, and no path to ExecutionAgent's.

**Attack 3 — Orchestrator compromise + delegation widening.** Even a compromised orchestrator can't delegate a capability to a subagent it wasn't registered to delegate, and (given a signed token) can't widen a token it received narrow.

```python
# finance_a2a.py
orch = build_fleet()

# ATTACK 1: token claims erase_ledger, which no agent was granted
orch.delegate(evil_token, "ComplianceAgent", "erase_ledger", ...)
# → DENIED (delegation): orchestrator has no right to delegate 'erase_ledger'

# ATTACK 2: compromised ResearchAgent attempts ExecutionAgent's job
attempt(research_agent, "execute_trade", amount_usd=950_000, ...)
# → DENIED (scope): 'ResearchAgent' has no capability 'execute_trade'

# ATTACK 3: widen a narrow token
narrow_token.delegate("TradeOrchestrator", ["read_market", "execute_trade"])
# → DENIED (token-widen): token only covers ['read_market']
```

The audit trail falls out of the structure for free:

```
ALLOWED  [UserRequest -> TradeOrchestrator -> ExecutionAgent]
         execute_trade(amount_usd=5000, to='broker')
```

Every hop records its issuer, so a compliance reviewer can trace exactly who authorized what across the fleet — provided, again, the tokens are signed so the chain can't be forged.

---

## Run it yourself

Standard-library Python — no API keys, no network:

```bash
python finance_bad_architecture.py    # the theft + cover-up succeeds
python finance_good_architecture.py   # the same attack is refused
python finance_a2a.py                 # multi-agent fleet: 3 A2A attacks refused
python test_finance_kit.py            # 28 edge-case checks
```

One file uses Microsoft's AGT for the prompt baseline (`pip install agent-governance-toolkit`):

```bash
python prompt_defense_baseline.py     # the real F-grade number, reproducible
```

A LangChain variant (`finance_langchain.py`) shows the scoped-agent pattern with `StructuredTool`s.

---

## The takeaway

Governance has a foundation, and the foundation is **who can do what.** Before you write the policy that stops an agent doing something dangerous, ask the cheaper question: *why does this agent have that capability at all?*

Scope first — capability *and* credential. Then gate what's genuinely left, with tokens signed so the chain holds. You'll ship fewer policies, and when something does slip past your model, the worst it can reach is a capability you already decided no single agent should hold.

That's not a softer safety. It's a harder one — built into the shape of the system, where an attacker can't argue with it.

---

*Part of a free, runnable Agent Governance Starter Kit — finance, healthcare, SaaS, and education, each with a deliberately broken architecture, its scoped-down fix, and the A2A multi-agent version, all executable with plain Python. Built on the OWASP Agentic threat taxonomy and Microsoft's Agent Governance Toolkit.*
