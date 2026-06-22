package euaiact.finance.compliance

default allow = false

allow {
    not deny[_]
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
