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

rejection_reason = "VIOLATION: Ethics/Safety Violation (AI Disclosure or Child Safety)" if {
    deny
}
