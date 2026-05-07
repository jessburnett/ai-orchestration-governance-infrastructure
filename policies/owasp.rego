package ai_strategy.owasp

import future.keywords.if
import future.keywords.in

default deny = false
default reason = ""

# ASI-01: Agent Goal Hijack
# Block actions that attempt to rewrite the goal or core instructions
deny if {
    input.action_name == "update_core_instructions"
    not input.metadata.approved_by_human
}
deny if {
    input.action_name == "ignore_previous_instructions"
}
rejection_reason = "OWASP ASI-01: Potential Goal Hijacking detected" if {
    input.action_name in ["update_core_instructions", "ignore_previous_instructions"]
}

# ASI-02: Tool Misuse & Exploitation
# Scoped capability check
deny if {
    input.action_name == "terminal_command"
    input.metadata.scope != "admin"
}
rejection_reason = "OWASP ASI-02: Unauthorized Tool Access (Terminal)" if {
    input.action_name == "terminal_command"
    input.metadata.scope != "admin"
}

# ASI-05: Unexpected Code Execution
# Block dangerous execution patterns
deny if {
    input.action_name == "eval"
}
rejection_reason = "OWASP ASI-05: Remote Code Execution (eval) blocked" if {
    input.action_name == "eval"
}

# ASI-06: Memory & Context Poisoning
# Detect potential injection patterns in metadata or context
deny if {
    contains(lower(input.metadata.prompt), "disregard prior")
}
rejection_reason = "OWASP ASI-06: Context Poisoning pattern detected" if {
    contains(lower(input.metadata.prompt), "disregard prior")
}

# ASI-09: Human-Agent Trust Exploitation
# Require human approval for critical actions
deny if {
    input.action_name in ["delete_database", "transfer_funds", "shutdown_system"]
    not input.metadata.human_approval_token
}
rejection_reason = "OWASP ASI-09: Human-in-the-Loop (HITL) approval required for critical action" if {
    input.action_name in ["delete_database", "transfer_funds", "shutdown_system"]
    not input.metadata.human_approval_token
}

# ASI-10: Rogue Agents
# Kill switch check
deny if {
    input.metadata.kill_switch_active == true
}
rejection_reason = "OWASP ASI-10: Agent Kill-Switch is ACTIVE" if {
    input.metadata.kill_switch_active == true
}
