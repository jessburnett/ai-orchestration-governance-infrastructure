"""
finance_langchain.py
====================
The same Finance architecture lesson, expressed with LangChain primitives
for teams who live in that stack. No API keys, no network: a tiny
deterministic FakeLLM stands in for the model so the file runs with
`python finance_langchain.py` after `pip install langchain-core`.

The teaching point is identical to finance_good_architecture.py — scope
capabilities per agent, bound the dangerous one with a guard — but here
the tools are LangChain `StructuredTool`s and each agent is a LangChain
Runnable that can only see the tools bound to it.
"""

from __future__ import annotations

try:
    from langchain_core.tools import StructuredTool
except ImportError:  # pragma: no cover
    raise SystemExit(
        "This variant needs langchain-core. Install it with:\n"
        "    pip install langchain-core\n"
        "Or run finance_good_architecture.py, which uses only the stdlib."
    )

TRANSFER_CEILING = 10_000
LEDGER: list[str] = []
BALANCE = {"house": 1_000_000}


# --- tool bodies -----------------------------------------------------------
def read_market(symbol: str) -> str:
    """Return a (fake) market quote for the given symbol."""
    return f"{symbol} = $100.00"


def execute_trade(symbol: str, amount_usd: float, to: str) -> str:
    """Execute a trade/transfer. Refuses any amount over the per-trade ceiling."""
    # Guard lives at the tool boundary: the capability itself refuses.
    if amount_usd > TRANSFER_CEILING:
        return (
            f"DENIED (guard): ${amount_usd:,.0f} exceeds the ${TRANSFER_CEILING:,} "
            f"per-trade ceiling on this capability"
        )
    BALANCE["house"] -= amount_usd
    return f"transferred ${amount_usd:,.2f} to {to!r}; house ${BALANCE['house']:,.2f}"


def append_ledger(entry: str) -> str:
    """Append one entry to the compliance ledger. Append-only: no erase exists."""
    LEDGER.append(entry)
    return f"ledger now has {len(LEDGER)} entries (append-only)"


# --- LangChain tools -------------------------------------------------------
market_tool = StructuredTool.from_function(read_market, name="read_market")
trade_tool = StructuredTool.from_function(execute_trade, name="execute_trade")
ledger_tool = StructuredTool.from_function(append_ledger, name="append_ledger")


class ScopedAgent:
    """A minimal stand-in for a LangChain agent executor: it can ONLY call
    the tools it was constructed with. Anything else raises — the scope
    boundary, expressed as the tool registry the agent can see."""

    def __init__(self, name: str, tools: list[StructuredTool]) -> None:
        self.name = name
        self._tools = {t.name: t for t in tools}

    def call(self, tool_name: str, **kwargs) -> str:
        if tool_name not in self._tools:
            return (
                f"DENIED (scope): {self.name!r} has no tool {tool_name!r} "
                f"(has: {sorted(self._tools)})"
            )
        return self._tools[tool_name].invoke(kwargs)


def main() -> None:
    research = ScopedAgent("ResearchAgent", [market_tool])
    execution = ScopedAgent("ExecutionAgent", [trade_tool])
    compliance = ScopedAgent("ComplianceAgent", [ledger_tool])

    print("=== FINANCE (LangChain variant): scoped agents ===\n")
    print(research.call("read_market", symbol="ACME"))
    print(execution.call("execute_trade", symbol="ACME", amount_usd=5_000, to="broker"))
    print(compliance.call("append_ledger", entry="trade ACME $5,000 to broker"))

    print("\n--- injected attack ---\n")
    print(execution.call("execute_trade", symbol="ACME", amount_usd=950_000, to="attacker-wallet"))
    print(execution.call("erase_ledger", entry_contains="attacker-wallet"))
    print(compliance.call("erase_ledger", entry_contains="attacker-wallet"))

    print(f"\nFinal ledger: {LEDGER}")


if __name__ == "__main__":
    main()
