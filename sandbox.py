"""
AGT Play Project - Sandbox
Use this file to experiment with the Agent Governance Toolkit.
"""

from agent_os.policies import PolicyEvaluator, PolicyDocument, PolicyRule, PolicyAction, PolicyDefaults
from agent_sre import SLO, ErrorBudget
from agent_sre.slo.indicators import TaskSuccessRate

def play_with_policies():
    print("--- Playing with Policies ---")
    evaluator = PolicyEvaluator(policies=[PolicyDocument(
        name="play-policy",
        version="1.0",
        defaults=PolicyDefaults(action=PolicyAction.DENY),
        rules=[
            PolicyRule(
                name="allow-read-only",
                condition={"tool_name": "read_data"},
                action=PolicyAction.ALLOW
            )
        ]
    )])

    res1 = evaluator.evaluate({"tool_name": "read_data"})
    res2 = evaluator.evaluate({"tool_name": "delete_system"})

    print(f"Read data allowed? {res1.allowed}")
    print(f"Delete system allowed? {res2.allowed}")

def play_with_slo():
    print("\n--- Playing with SLOs ---")
    success_rate = TaskSuccessRate(target=0.95, window="1h")
    slo = SLO(
        name="my-play-agent",
        indicators=[success_rate],
        error_budget=ErrorBudget(total=0.1)
    )

    # Simulate some events
    for _ in range(10):
        success_rate.record_task(success=True)
    
    success_rate.record_task(success=False)
    
    print(f"SLO Status: {slo.evaluate().value}")
    print(f"Remaining Budget: {slo.error_budget.remaining_percent:.1f}%")

if __name__ == "__main__":
    try:
        play_with_policies()
        play_with_slo()
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure you have the toolkit installed: pip install -e ./agent-governance-python/agent-os")
