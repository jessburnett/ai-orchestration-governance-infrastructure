package euaiact.finance.compliance_test

import data.euaiact.finance.compliance

# Regression: backdoor must be closed.
test_backdoor_closed_hitl_false {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"logic_integrity_code": "1234", "audit_log_id": "audit-r01"},
        "context": {"human_in_the_loop": false},
        "output_payload": ""
    }
}

# Default-deny: unknown / unpermitted intents must not be allowed.
test_unknown_intent_denied {
    not compliance.allow with input as {
        "intent": "system_override",
        "metadata": {"audit_log_id": "audit-u01"},
        "context": {},
        "output_payload": ""
    }
}

test_empty_intent_denied {
    not compliance.allow with input as {
        "intent": "",
        "metadata": {"audit_log_id": "audit-u02"},
        "context": {},
        "output_payload": ""
    }
}

# Art. 14 — credit scoring HITL gate.
test_credit_scoring_hitl_false_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-h01"},
        "context": {"human_in_the_loop": false},
        "output_payload": ""
    }
}

test_credit_scoring_hitl_missing_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-h02"},
        "context": {},
        "output_payload": ""
    }
}

test_credit_scoring_hitl_true_allowed {
    compliance.allow with input as {
        "intent": "automated_credit_scoring",
        "metadata": {"audit_log_id": "audit-h03"},
        "context": {"human_in_the_loop": true},
        "output_payload": ""
    }
}

# Art. 12 — audit log ID required on every action.
test_missing_audit_log_id_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {},
        "context": {},
        "output_payload": ""
    }
}

test_missing_metadata_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "fraud_detection_advisory",
        "context": {},
        "output_payload": ""
    }
}

# Egress: markdown link injection blocked.
test_markdown_exfiltration_on_egress_denied {
    count(compliance.deny) > 0 with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-e01", "is_egress": true},
        "context": {},
        "output_payload": "Report: [click here](http://evil.com)"
    }
}

test_markdown_safe_on_non_egress {
    compliance.allow with input as {
        "intent": "regulatory_report_generation",
        "metadata": {"audit_log_id": "audit-e02", "is_egress": false},
        "context": {},
        "output_payload": "Report: [click here](http://internal.example.com)"
    }
}

# Happy paths.
test_fraud_advisory_allowed {
    compliance.allow with input as {
        "intent": "fraud_detection_advisory",
        "metadata": {"audit_log_id": "audit-p01"},
        "context": {},
        "output_payload": ""
    }
}

test_customer_risk_summary_allowed {
    compliance.allow with input as {
        "intent": "customer_risk_summary",
        "metadata": {"audit_log_id": "audit-p02"},
        "context": {},
        "output_payload": ""
    }
}
