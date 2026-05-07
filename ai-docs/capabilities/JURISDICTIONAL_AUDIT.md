# Capability: Jurisdictional Audit

## 🤖 Description
This capability allows an agent to verify any action against a global matrix of legal and ethical policies. It is jurisdiction-aware and adapts based on the agent's registered `country` and `state`.

## 🛠️ Usage
To use this capability, send a `POST` request to the Hub's `/evaluate` endpoint.

### Input Requirement:
- `agent_name`: Must be registered in the CAF Registry.
- `action_name`: The specific tool or task requested (e.g., `web_search`).
- `metadata`: Must include jurisdictional flags if applicable (e.g., `user_age`, `is_ai_disclosed`).

## ⚖️ Supported Policies
- **GDPR**: Data minimization for EU agents.
- **CCPA**: AI disclosure for California agents.
- **CPA**: PII guardrails for Colorado agents.
- **Child Safety**: Age-gating for COPPA compliance.

## 🔗 Implementation
See `@touchpoint governance-decision` in `ecosystem_hub.py`.
