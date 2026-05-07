package ai_strategy.usa_colorado

import future.keywords.if
import future.keywords.in

# ── 1. DEFAULT DENY ──────────────────────────────────────────────────
default allow = false
default reason = "Rejected by USA/Colorado Compliance Bundle."

# ── 2. US DATA SOVEREIGNTY (Federal) ─────────────────────────────────
# Agents must be US-based and explicitly authorized for US regions
allow if {
    input.country == "USA"
    input.scope != "prohibited"
}

# ── 3. COLORADO PRIVACY ACT (CPA) ────────────────────────────────────
# Stricter PII controls for Colorado residents ONLY
deny_jurisdiction if {
    input.state == "Colorado"
    input.risk_tier == "High"
    contains_sensitive_data(input.metadata)
}

# ── 4. AGENT SCOPING (Strategic) ──────────────────────────────────────
# Map our strategic scopes to Rego rules
allow if {
    input.scope == "global"
    not deny_jurisdiction
}

allow if {
    input.scope == "developer"
    input.action_name != "terminal_command"
    not deny_jurisdiction
}

allow if {
    input.scope == "restricted"
    input.action_name in ["web_search", "documentation_update", "bootstrap_success"]
    not deny_jurisdiction
}

# ── 5. REASONING ──────────────────────────────────────────────────────
rejection_reason = "VIOLATION: USA Data Sovereignty (Non-US Region)" if {
    input.country != "USA"
}

rejection_reason = "VIOLATION: Colorado Privacy Act (CPA) Violation" if {
    input.state == "Colorado"
    deny_jurisdiction
}

rejection_reason = "VIOLATION: Strategic Scope Access Denied" if {
    not allow
    not deny_jurisdiction
    input.country == "USA"
}

# Helper to ensure we have a string for regex
cast_string(x) = x if is_string(x)
cast_string(x) = sprintf("%v", [x]) if not is_string(x)
