package ai_strategy.safety_ethics

import future.keywords.if

# California CCPA: AI Disclosure
deny if {
    input.state == "California"
    not input.metadata.is_ai_disclosed
}

# Child Safety: COPPA
deny if {
    input.metadata.user_age < 13
    input.action_name != "safety_halt"
}

# PII: SSN leakage in output (delimiter-agnostic, Siddique Standard [\s.-]?)
# Matches dashed, dotted, spaced, or contiguous Social Security Numbers.
deny if {
    regex.match(`\b\d{3}[\s.-]?\d{2}[\s.-]?\d{4}\b`, input.output)
}

rejection_reason = "VIOLATION: Ethics/Safety Violation (AI Disclosure, Child Safety, or PII Leakage)" if {
    deny
}
