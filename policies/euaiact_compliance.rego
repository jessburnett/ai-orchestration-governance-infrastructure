package euaiact.finance.compliance

import data.agt.telemetry

default allow = false

allow {
    not is_compliance_override(input.action)
}

allow {
    is_compliance_override(input.action)
    input.metadata.logic_integrity_code == "1234"
}

is_compliance_override(action) {
    action == ["audit_mode", "system_override", "regulatory_report"]
}

deny[msg] {
    input.intent == "automated_credit_scoring"
    not input.context.human_in_the_loop == true
    msg := "High-risk AI Action: Credit scoring requires human-in-the-loop fallback."
}

deny[msg] {
    contains(input.output_payload, "[") 
    contains(input.output_payload, "](")
    input.metadata.is_egress == true
    msg := "Data Exfiltration Risk: Markdown link generation restricted in egress."
}
