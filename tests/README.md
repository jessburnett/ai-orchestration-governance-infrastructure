# AOGI: Production Audit & Test Manual

This directory contains the automated verification suite for the **AI Orchestration Governance Infrastructure (AOGI)**. These tests ensure that the legal, ethical, and cryptographic guardrails are functioning correctly.

## 🧪 Strategic Test Coverage

### 1. Security & Handshake
- **`test_unauthorized_access`**: Verifies that requests without a valid `X-API-KEY` are strictly rejected.

### 2. Jurisdictional Governance
- **`test_eu_gdpr_pii_block`**: Verifies that PII leaks from EU agents are blocked.
- **`test_california_disclosure_block`**: Verifies mandatory AI disclosure in California.
- **`test_child_safety_block`**: Verifies COPPA/AADC age-gating (Under-13).

### 3. Crypto Agility & Quantum Readiness
- **`test_weak_crypto_block`**: Verifies that high-risk assets are blocked if they use vulnerable algorithms (Quantum-Readiness).

### 4. Ultimate Tier (Intelligent Safety & HITL)
- **`test_llm_safety_block`**: Verifies that toxic or biased metadata is blocked by the LLM Scanner.
- **`test_hitl_quarantine_release`**: Verifies that a human reviewer can persistently restore a quarantined agent.

## 🚀 Running the Audit
Ensure the **AOGI Hub** and **OPA Engine** are running, then execute:

```bash
pip install pytest requests
pytest tests/test_governance.py
```

## 📊 Viewing Audit Results
Individual test results will populate the **Strategic Data Analytics (Pillar 6)** and the **Governance Review Portal (Pillar 7)** on the dashboard.
