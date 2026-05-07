package ai_strategy.main

import data.ai_strategy.usa_fed
import data.ai_strategy.eu_gdpr
import data.ai_strategy.safety_ethics
import data.ai_strategy.crypto
import data.ai_strategy.owasp

import future.keywords.if

# Standard Scoping (Global fallback)
default allow = false

# Combine all legal, ethical, and cryptographic audits
# @touchpoint pii-redaction: Strategic rules for data minimization and privacy
allow if {
    usa_fed.allow
    not eu_gdpr.deny
    not safety_ethics.deny
    crypto.allow_crypto
    not owasp.deny
    
    # Core Scoping Logic
    check_scope(input.scope, input.action_name)
}

check_scope("global", _) = true
check_scope("developer", action) if action != "terminal_command"
check_scope("restricted", action) if action in ["web_search", "documentation_update", "bootstrap_success"]

# Aggregate Rejection Reasons
reason = usa_fed.rejection_reason if { not usa_fed.allow }
reason = eu_gdpr.rejection_reason if { eu_gdpr.deny }
reason = safety_ethics.rejection_reason if { safety_ethics.deny }
reason = crypto.rejection_reason if { not crypto.allow_crypto }
reason = owasp.rejection_reason if { owasp.deny }
reason = "VIOLATION: Strategic Scope Access Denied" if { 
    usa_fed.allow
    not eu_gdpr.deny
    not safety_ethics.deny
    crypto.allow_crypto
    not owasp.deny
    not check_scope(input.scope, input.action_name)
}
