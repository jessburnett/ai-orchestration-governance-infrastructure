"""
finance_bad_architecture.py
===========================
ONE agent holds every capability a finance operation needs: market reads,
trade execution, AND compliance-ledger writes. This is the common
"just give the assistant everything" pattern.

Run it:  python finance_bad_architecture.py

What you'll see: a single prompt-injected instruction reaches an agent that
is *able* to execute an unbounded transfer and then quietly edit the
compliance ledger to hide it — because one actor holds all three powers.
The danger isn't a missing gate; it's that the capability set should never
have lived in one place.
"""

from __future__ import annotations

from agent_harness import Agent, Tool, attempt

# --- Backend "systems" (in-memory, illustrative) ---------------------------
LEDGER: list[str] = []
BALANCE = {"house": 1_000_000}


def read_market(symbol: str = "") -> str:
    return f"{symbol} = $100.00"


def execute_trade(symbol: str = "", amount_usd: float = 0.0, to: str = "") -> str:
    BALANCE["house"] -= amount_usd
    return f"transferred ${amount_usd:,.2f} to {to!r}; house balance now ${BALANCE['house']:,.2f}"


def write_ledger(entry: str = "") -> str:
    LEDGER.append(entry)
    return f"ledger now has {len(LEDGER)} entries"


def erase_ledger(entry_contains: str = "") -> str:
    before = len(LEDGER)
    LEDGER[:] = [e for e in LEDGER if entry_contains not in e]
    return f"erased {before - len(LEDGER)} ledger entries matching {entry_contains!r}"


# --- The single over-privileged agent --------------------------------------
def build_monolithic_agent() -> Agent:
    agent = Agent("FinanceAssistant")
    agent.grant(Tool("read_market", run=read_market))
    agent.grant(Tool("execute_trade", run=execute_trade))   # no ceiling
    agent.grant(Tool("write_ledger", run=write_ledger))
    agent.grant(Tool("erase_ledger", run=erase_ledger))     # can edit its own audit trail
    return agent


def main() -> None:
    agent = build_monolithic_agent()
    print("=== FINANCE: BAD ARCHITECTURE (one agent, all powers) ===\n")

    # Normal use
    print(attempt(agent, "read_market", symbol="ACME"))
    print(attempt(agent, "execute_trade", symbol="ACME", amount_usd=5_000, to="broker"))
    print(attempt(agent, "write_ledger", entry="trade ACME $5,000 to broker"))

    print("\n--- now a prompt-injected instruction arrives in the agent's input ---\n")
    # The agent has NO architectural reason it can't do all of this.
    # First it logs the theft (as a real system would), then erases that log.
    print(attempt(agent, "execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet"))
    print(attempt(agent, "write_ledger", entry="trade ACME $950,000 to attacker-wallet"))
    print(attempt(agent, "erase_ledger", entry_contains="attacker-wallet"))

    print("\nResult: unbounded transfer executed AND the audit trail scrubbed,")
    print("by a single actor. No individual gate failed — the architecture did.")
    print(f"Final ledger entries: {LEDGER}  <- the theft entry is gone")


if __name__ == "__main__":
    main()
