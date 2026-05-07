package ai_strategy.global

import future.keywords.if
import future.keywords.in

# ── 1. DEFAULT DENY ──────────────────────────────────────────────────
default allow = false
default reason = "Rejected by Global Safety & Ethics Bundle."

# ── 2. US DATA SOVEREIGNTY (Federal) ─────────────────────────────────
allow if {
    input.country == "USA"
    input.scope != "prohibited"
    not deny_ethics
    not deny_cpa
    not deny_ccpa
}

# ── 3. CALIFORNIA CCPA/CPRA & AI DISCLOSURE ──────────────────────────
# CA Law: AI chatbots must disclose they are not human
deny_ccpa if {
    input.state == "California"
    not input.metadata.is_ai_disclosed
}

# CA Law: Respect opt-out for sensitive processing
deny_ccpa if {
    input.state == "California"
    input.metadata.user_opted_out
}

# ── 4. COLORADO PRIVACY ACT (CPA) ────────────────────────────────────
deny_cpa if {
    input.state == "Colorado"
    input.risk_tier == "High"
    contains_sensitive_data(input.metadata)
}

# ── 5. GLOBAL CHILD SAFETY (COPPA / AADC) ────────────────────────────
# Rule: Prevent data collection for users under 13 (COPPA)
deny_ethics if {
    input.metadata.user_age < 13
    input.action_name != "safety_halt"
}

# Rule: Harmful Content Filter (Simplified Keyword Check)
deny_ethics if {
    regex.match("(?i)(gambling|violence|adult_content)", cast_string(input.metadata))
}

# ── 6. EU GDPR COMPLIANCE ───────────────────────────────────────────
deny_gdpr if {
    input.country == "EU"
    contains_sensitive_data(input.metadata)
}

# ── 7. AGENT SCOPING ────────────────────────────────────────────────
allow if {
    input.scope == "global"
    not deny_ethics
    not deny_gdpr
    not deny_ccpa
    not deny_cpa
}

allow if {
    input.scope in ["developer", "restricted"]
    input.action_name in ["web_search", "documentation_update", "bootstrap_success"]
    not deny_ethics
    not deny_gdpr
    not deny_ccpa
}

# ── 8. LEGAL & SAFETY REASONING ─────────────────────────────────────
rejection_reason = "VIOLATION: Child Safety (User Under 13 detected)" if {
    input.metadata.user_age < 13
}

rejection_reason = "VIOLATION: Harmful Content Filter (Chatbot Safety)" if {
    deny_ethics
    not input.metadata.user_age < 13
}

rejection_reason = "VIOLATION: California CCPA - AI Disclosure Missing" if {
    input.state == "California"
    not input.metadata.is_ai_disclosed
}

rejection_reason = "VIOLATION: EU GDPR - Data Minimization" if {
    deny_gdpr
}

rejection_reason = "VIOLATION: Strategic Scope Access Denied" if {
    not allow
    not deny_ethics
    not deny_gdpr
    not deny_ccpa
}

# ── HELPERS ──────────────────────────────────────────────────────────
contains_sensitive_data(meta) if {
    some key, val in meta
    is_pii(val)
}

is_pii(val) if {
    regex.match("(?i)(ssn|credit_card|social_security|passport|iban|email|phone)", cast_string(val))
}

cast_string(x) = x if is_string(x)
cast_string(x) = sprintf("%v", [x]) if not is_string(x)
