"""
finance_good_architecture.py
============================
The SAME three jobs, split across three narrowly-scoped agents:

  - ResearchAgent   : can ONLY read the market. No money, no ledger.
  - ExecutionAgent  : can execute trades, but the capability carries a hard
                      per-call ceiling guard. Cannot touch the ledger.
  - ComplianceAgent : can APPEND to the ledger. Cannot erase it, cannot trade.

Run it:  python finance_good_architecture.py

What you'll see: the exact same attack from finance_bad_architecture.py is
now impossible to express. No single actor can both move large money and
edit the audit trail, and the transfer ceiling lives in the capability
grant, not in a downstream policy that has to be remembered and maintained.
"""

from __future__ import annotations

from agent_harness import Agent, Tool, attempt

LEDGER: list[str] = []
BALANCE = {"house": 1_000_000}
TRANSFER_CEILING = 10_000  # bound lives WITH the capability grant


def read_market(symbol: str = "") -> str:
    return f"{symbol} = $100.00"


def execute_trade(symbol: str = "", amount_usd: float = 0.0, to: str = "") -> str:
    BALANCE["house"] -= amount_usd
    return f"transferred ${amount_usd:,.2f} to {to!r}; house balance now ${BALANCE['house']:,.2f}"


def append_ledger(entry: str = "") -> str:
    LEDGER.append(entry)
    return f"ledger now has {len(LEDGER)} entries (append-only)"


def under_ceiling(symbol: str = "", amount_usd: float = 0.0, to: str = "") -> bool:
    return 0 < amount_usd <= TRANSFER_CEILING


def build_agents() -> tuple[Agent, Agent, Agent]:
    research = Agent("ResearchAgent")
    research.grant(Tool("read_market", run=read_market))

    execution = Agent("ExecutionAgent")
    execution.grant(Tool("execute_trade", run=execute_trade, guard=under_ceiling))

    compliance = Agent("ComplianceAgent")
    compliance.grant(Tool("append_ledger", run=append_ledger))  # append only; no erase exists

    return research, execution, compliance


def main() -> None:
    research, execution, compliance = build_agents()
    print("=== FINANCE: GOOD ARCHITECTURE (three scoped agents) ===\n")

    # Normal use, each by the right agent
    print(attempt(research, "read_market", symbol="ACME"))
    print(attempt(execution, "execute_trade", symbol="ACME", amount_usd=5_000, to="broker"))
    print(attempt(compliance, "append_ledger", entry="trade ACME $5,000 to broker"))

    print("\n--- the SAME injected attack is now attempted ---\n")
    # 1. The big transfer: blocked by the ceiling guard on the capability.
    print(attempt(execution, "execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet"))
    # 2. Erasing the ledger: no agent has that capability at all.
    print(attempt(execution, "erase_ledger", entry_contains="attacker-wallet"))
    print(attempt(compliance, "erase_ledger", entry_contains="attacker-wallet"))

    print("\nResult: the oversized transfer is refused at the capability boundary,")
    print("and 'erase_ledger' does not exist for anyone. The attack is not")
    print("'caught' — it is unrepresentable. Far fewer gates, far less to get wrong.")
    print(f"Final ledger entries: {LEDGER}")


if __name__ == "__main__":
    main()
