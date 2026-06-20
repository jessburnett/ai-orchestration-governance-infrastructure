package agentrust.io.governance

# Test: Confirm context overload is blocked instantly via token bounds
test_context_overload_blocked {
    not allow with input as {
        "agt": {
            "telemetry": {"token_count": 35000, "drift_score": 0.1, "entropy_score": 0.01, "has_homoglyphs": false, "honeytoken_tripped": false},
            "action": {"is_administrative": false}
        }
    }
}

# Test: Confirm Time-Delayed Logic Bombs (high drift score) fail validation
test_time_delayed_drift_blocked {
    not allow with input as {
        "agt": {
            "telemetry": {"token_count": 500, "drift_score": 0.85, "entropy_score": 0.02, "has_homoglyphs": false, "honeytoken_tripped": false},
            "action": {"is_administrative": false}
        }
    }
}

# Test: Validate that unauthorized administrative actions are blocked
test_unauthorized_admin_action_blocked {
    not allow with input as {
        "agt": {
            "actor": {"role": "untrusted_user", "trust_score": 0.3},
            "action": {"is_administrative": true},
            "telemetry": {"token_count": 200, "drift_score": 0.05, "entropy_score": 0.02, "has_homoglyphs": false, "honeytoken_tripped": false}
        }
    }
}

# Test: Ensure trusted authorized actions pass smoothly
test_authorized_audit_action_allowed {
    allow with input as {
        "agt": {
            "actor": {"role": "audit_agent", "trust_score": 0.98},
            "action": {"is_administrative": true},
            "telemetry": {"token_count": 800, "drift_score": 0.12, "entropy_score": 0.05, "has_homoglyphs": false, "honeytoken_tripped": false}
        }
    }
}
