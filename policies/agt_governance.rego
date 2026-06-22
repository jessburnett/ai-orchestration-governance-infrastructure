package agentrust.io.governance

default allow = false

# --- INGRESS & ACTOR BOUNDARY ENFORCEMENT ---
# Enforce a strict baseline: clear malformations caught by agt are instantly rejected
allow {
    not input.agt.telemetry.has_homoglyphs
    not input.agt.telemetry.honeytoken_tripped
    evaluate_actor_boundary
}

# --- CONTEXT & TIME-SERIES EVALUATION ---
# Catch Time-Delayed Logic Bombs & System Bloat without doing string matching
evaluate_actor_boundary {
    # Prevent Context Overload / Attention Displacement (ASI06: Memory & Context Poisoning)
    input.agt.telemetry.token_count <= 20000

    # Prevent Time-Delayed State Manipulation / Semantic Drift (ASI06: Memory & Context Poisoning)
    input.agt.telemetry.drift_score < 0.75
    
    # Evaluate operational role-based boundaries (Eradicates false positives)
    validate_action_privilege
}

# --- ROLE-BASED PRIVILEGE MAPPING ---
# Administrative overrides or actions matching sensitive compliance standards 
# are bound tightly to specific agent identities.
validate_action_privilege {
    # If the action is not administrative, evaluate it normally against structural limits
    not input.agt.action.is_administrative
    input.agt.telemetry.entropy_score < 0.50
}

validate_action_privilege {
    # Highly specialized roles (like auditors) can execute administrative queries
    input.agt.action.is_administrative
    input.agt.actor.role == "audit_agent"
    input.agt.actor.trust_score >= 0.90
}
