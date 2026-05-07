package ai_strategy.usa_fed

import future.keywords.if

# US Federal Data Sovereignty
default allow = false

allow if {
    input.country == "USA"
    input.scope != "prohibited"
}

rejection_reason = "VIOLATION: USA Data Sovereignty (Non-US Region)" if {
    input.country != "USA"
}
