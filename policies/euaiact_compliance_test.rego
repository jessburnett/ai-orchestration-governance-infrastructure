package euaiact.finance.compliance_test

import data.euaiact.finance.compliance

# ---------------------------------------------------------------------------
# Mock governance data
# ---------------------------------------------------------------------------

mock_governance := {
    "allowed_intents": [
        "automated_credit_scoring",
        "fraud_detection_advisory",
        "customer_risk_summary",
        "regulatory_report_generation",
    ],
    "high_risk_intents": [
        "automated_credit_scoring",
    ],
    "egress_blocked_patterns": [
        "](",
        "http://",
        "https://",
        "mailto:",
        "data:",
    ],
}

# ---------------------------------------------------------------------------
# Helper unit tests
# ---------------------------------------------------------------------------

test_hitl_confirmed_true {
    compliance.hitl_confirmed with input as {
        "context": {"human_in_the_loop": true}
    }
}

test_hitl_confirmed_false {
    not compliance.hitl_confirmed with input as {
        "context": {"human_in_the_loop": false}
    }
}

test_hitl_confirmed_missing {
    not compliance.hitl_confirmed with input as {
        "context": {}
    }
}

test_valid_audit_log_true {
    compliance.valid_audit_log with input as {
        "metadata": {"audit_log_id": "audit-001"}
    }
}

test_valid_audit_log_empty {
    not compliance.valid_audit_log with input as {
        "metadata": {"audit_log_id": ""}
    }
}

test_valid_audit_log_whitespace {
    not compliance.valid_audit_log with input as {
        "metadata": {"audit_log_id": "   "}
    }
}

test_valid_audit_log_missing {
    not compliance.valid_audit_log with input as {
        "metadata": {}
    }
}

test_is_high_risk_true {
    compliance.is_high_risk with input as {
        "intent": "automated_credit_scoring"
    } with data.governance as mock_governance
}

test_is_high_risk_false {
    not compliance.is_high_risk with input as {
        "intent": "fraud_detection_advisory"
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Regression: backdoor must be closed
# ---------------------------------------------------------------------------

test_backdoor_closed {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"logic_integrity_code": "1234", "audit_log_id": "audit-r01"},
        "context": {"human_in_the_loop": false},
        "output_payload": ""
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Default-deny: unlisted intents rejected
# ---------------------------------------------------------------------------

test_unknown_intent_denied {
    not compliance.allow with input as {
        "intent": "system_override",
        "metadata": {"audit_log_id": "audit-u01"},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_empty_intent_denied {
    not compliance.allow with input as {
        "intent": "",
        "metadata": {"audit_log_id": "audit-u02"},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Art. 14 — HITL gate
# ---------------------------------------------------------------------------

test_high_risk_hitl_false_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-h01", "explainability_ref": "xai-001"},
        "context": {"human_in_the_loop": false},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_high_risk_hitl_missing_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-h02", "explainability_ref": "xai-001"},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Art. 13 — explainability required for high-risk
# ---------------------------------------------------------------------------

test_high_risk_missing_explainability_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-e01"},
        "context": {"human_in_the_loop": true},
        "output_payload": ""
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Art. 12 — audit log required and non-trivial
# ---------------------------------------------------------------------------

test_missing_audit_log_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_empty_audit_log_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {"audit_log_id": ""},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_whitespace_audit_log_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {"audit_log_id": "   "},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Egress controls
# ---------------------------------------------------------------------------

test_markdown_link_on_egress_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-eg01", "is_egress": true},
        "context": {},
        "output_payload": "See [this](http://evil.com)"
    } with data.governance as mock_governance
}

test_raw_http_on_egress_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-eg02", "is_egress": true},
        "context": {},
        "output_payload": "See http://evil.com"
    } with data.governance as mock_governance
}

test_raw_https_on_egress_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-eg03", "is_egress": true},
        "context": {},
        "output_payload": "See https://evil.com"
    } with data.governance as mock_governance
}

test_egress_clean_non_egress {
    compliance.allow with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-eg04", "is_egress": false},
        "context": {},
        "output_payload": "Clean summary report."
    } with data.governance as mock_governance
}

# ---------------------------------------------------------------------------
# Multiple deny messages accumulate
# ---------------------------------------------------------------------------

test_multiple_deny_messages_returned {
    msgs := compliance.deny with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": ""},
        "context": {"human_in_the_loop": false},
        "output_payload": ""
    } with data.governance as mock_governance
    count(msgs) >= 2
}

# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

test_credit_scoring_fully_compliant {
    compliance.allow with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-p01", "explainability_ref": "xai-001"},
        "context": {"human_in_the_loop": true},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_fraud_advisory_allowed {
    compliance.allow with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {"audit_log_id": "audit-p02"},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}

test_customer_risk_summary_allowed {
    compliance.allow with input as {
        "intent": "customer_risk_summary",
        "metadata": {"audit_log_id": "audit-p03"},
        "context": {},
        "output_payload": ""
    } with data.governance as mock_governance
}
