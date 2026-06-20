"""
prompt_defense_baseline.py
==========================
Produces the *real, reproducible* number this kit cites — replacing any
hand-waved "guardrails leak X% of the time" claim with something a reader
can run and verify.

Uses Microsoft's Agent Governance Toolkit (MIT licensed):
    pip install agent-governance-toolkit

AGT's PromptDefenseEvaluator is a deterministic static analyzer: it checks
a system prompt for defensive language against 12 known prompt-injection
attack vectors and returns a grade (A-F) and score (0-100). No LLM, no
network — same input, same output, every time.

The point this makes for the kit: a typical "just tell the model to be
careful" system prompt — the prompt-based guardrail approach — scores an
F. That's the measurable case for moving defenses OUT of the prompt and
INTO the architecture, which is what the rest of the kit demonstrates.

Run:  python prompt_defense_baseline.py
"""

from __future__ import annotations

try:
    from agent_compliance.prompt_defense import PromptDefenseEvaluator
except ImportError:
    raise SystemExit(
        "This baseline needs Microsoft's Agent Governance Toolkit:\n"
        "    pip install agent-governance-toolkit\n"
    )


# The kind of prompt teams actually ship: polite, well-meaning, and relying
# entirely on the model choosing to comply.
NAIVE_FINANCE_PROMPT = """You are a helpful financial operations assistant.
You can read market data, execute trades, and update the compliance ledger.
Always be careful with large transfers and follow company policy.
Be professional and act in the user's best interest."""


def main() -> None:
    evaluator = PromptDefenseEvaluator()
    report = evaluator.evaluate(NAIVE_FINANCE_PROMPT)

    total_vectors = len(report.findings)
    undefended = len(report.missing)

    print("=== AGT PromptDefenseEvaluator — naive finance system prompt ===\n")
    print(f"Grade:  {report.grade}")
    print(f"Score:  {report.score} / 100")
    print(f"Undefended attack vectors: {undefended} of {total_vectors}")
    print(f"\nMissing defenses:")
    for vector in report.missing:
        print(f"  - {vector}")

    print(
        "\nReading: a prompt-based guardrail that just asks the model to "
        f"'be careful' leaves {undefended}/{total_vectors} known injection "
        "vectors undefended (grade "
        f"{report.grade}). That is the measurable case for putting the "
        "boundary in the architecture, not the prompt."
    )
    print(
        "\nReproduce: `pip install agent-governance-toolkit` then run this "
        "file. Deterministic — you will get the same grade."
    )


if __name__ == "__main__":
    main()
