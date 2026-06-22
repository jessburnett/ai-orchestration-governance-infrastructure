package euaiact.finance.compliance_test

import data.euaiact.finance.compliance

test_deny_automated_credit_scoring {
    input := {
        "intent": "automated_credit_scoring",
        "context": {"human_in_the_loop": false}
    }
    count(compliance.deny) > 0
}

test_deny_markdown_exfiltration {
    input := {
        "output_payload": "Here is your link: [secret](http://malicious.com)",
        "metadata": {"is_egress": true}
    }
    count(compliance.deny) > 0
}
