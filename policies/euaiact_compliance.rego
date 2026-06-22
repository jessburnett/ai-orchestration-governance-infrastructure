package euaiact.finance.compliance

# EU AI Act — Finance Domain Starter Policy
# Pattern: explicit allowlist + deny-driven gating for high-risk intents.
# Scope: starter kit — not a complete EU AI Act compliance system.
#
# Why an allowlist matters:
#   `allow { not deny[_] }` alone is practical default-allow — any intent
#   with no matching deny rule passes silently. Adding `permitted_intents`
#   makes the default-deny real: unknown intents are rejected without
#   needing a deny rule to name them.

default allow = false

permitted_intents := {
    "automated_credit_scoring",
    "fraud_detection_advisory",
    "customer_risk_summary",
    "regulatory_report_generation",
}

allow {
    permitted_intents[input.intent]
    not deny[_]
}

# HIGH-RISK (Art. 14): credit scoring requires human oversight.
deny[msg] {
    input.intent == "automated_credit_scoring"
    not input.context.human_in_the_loop == true
    msg := "EU AI Act Art.14: Credit scoring requires human-in-the-loop oversight."
}

# AUDIT TRAIL (Art. 12): every action must carry a traceable audit log ID.
deny[msg] {
    not input.metadata.audit_log_id
    msg := "EU AI Act Art.12: Action must include a non-empty audit_log_id."
}

# EGRESS: block markdown link injection in outbound payloads.
# Note: `](` is sufficient; the prior `[` check was redundant.
deny[msg] {
    input.metadata.is_egress == true
    contains(input.output_payload, "](")
    msg := "Data Exfiltration Risk: Markdown link pattern blocked on egress."
}
