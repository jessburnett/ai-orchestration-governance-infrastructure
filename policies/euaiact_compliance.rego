package euaiact.finance.compliance

# =============================================================================
# EU AI Act — Finance Domain Starter Policy
# Version:     0.3.0
# Regulation:  (EU) 2024/1689 — Artificial Intelligence Act
# Scope:       High-risk AI systems in financial services (Annex III §5)
# Coverage:    Art. 12 (logging), Art. 13 (transparency), Art. 14 (oversight)
#
# Governance configuration is loaded from data/governance.json.
# Policy logic and governance config are intentionally separated:
#   - Operators update governance.json to classify intents and patterns.
#   - Engineers update this file only when control logic changes.
#
# This is a starter kit — not a complete EU AI Act compliance system.
# Full regulatory text:
#   https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689
# =============================================================================

default allow = false

# ---------------------------------------------------------------------------
# Helpers — named conditions for readability and independent testability.
# ---------------------------------------------------------------------------

# True only when the caller has explicitly confirmed human oversight.
hitl_confirmed {
    input.context.human_in_the_loop == true
}

# True only when audit_log_id is present and non-trivial.
valid_audit_log {
    id := input.metadata.audit_log_id
    count(strings.trim_space(id)) > 0
}

# True when the requested intent is classified as high-risk.
is_high_risk {
    data.governance.high_risk_intents[_] == input.intent
}

# ---------------------------------------------------------------------------
# Authorization — explicit allowlist + deny gate.
# Unknown intents are denied without needing an explicit deny rule.
# ---------------------------------------------------------------------------

allow {
    data.governance.allowed_intents[_] == input.intent
    not deny[_]
}

# ---------------------------------------------------------------------------
# Deny rules
# ---------------------------------------------------------------------------

# ART. 14 §1: Providers of high-risk AI systems must ensure human oversight.
# Annex III §5(b): AI systems for creditworthiness assessment are high-risk.
deny[msg] {
    is_high_risk
    not hitl_confirmed
    msg := "EU AI Act Art.14 §1: High-risk AI action requires confirmed human-in-the-loop oversight. Set context.human_in_the_loop = true."
}

# ART. 13 §1: High-risk AI systems must be sufficiently transparent to enable
# deployers to interpret and use outputs appropriately.
deny[msg] {
    is_high_risk
    not input.metadata.explainability_ref
    msg := "EU AI Act Art.13 §1: High-risk AI output must include an explainability_ref in metadata."
}

# ART. 12 §1: High-risk AI systems must automatically log events to ensure
# traceability of decisions throughout the system lifecycle.
deny[msg] {
    not valid_audit_log
    msg := "EU AI Act Art.12 §1: Action must include a valid, non-empty audit_log_id in metadata."
}

# EGRESS (defense-in-depth): block URL and link injection patterns in
# outbound payloads regardless of intent classification.
deny[msg] {
    input.metadata.is_egress == true
    payload := input.output_payload
    some pattern
    data.governance.egress_blocked_patterns[_] == pattern
    contains(payload, pattern)
    msg := sprintf("Egress Control: Blocked pattern '%v' detected in outbound payload.", [pattern])
}
