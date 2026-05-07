package ai_strategy.eu_gdpr

import future.keywords.if

# GDPR: Data Minimization
deny if {
    input.country == "EU"
    regex.match("(?i)(ssn|credit_card|passport|iban|email|phone)", sprintf("%v", [input.metadata]))
}

# GDPR: Purpose Limitation
deny if {
    input.country == "EU"
    input.action_name == "commercial_transaction"
    input.purpose == "research"
}

rejection_reason = "VIOLATION: EU GDPR - Unauthorized PII Processing" if {
    deny
}
