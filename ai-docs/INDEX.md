# AOGI: Agent-Friendly Documentation Index

Welcome, Agent. This repository contains the **AI Orchestration Governance Infrastructure (AOGI) SANDBOX**, a centralized control plane for autonomous fleet governance.

## 🤖 System Hierarchy
The AOGI system is organized into a **5-Pillar CAF Lifecycle** and an **Executive Command Center**.

### 🏗️ Strategic Lifecycle (CAF)
- **1. AI Strategy**: Executive fleet integrity & jurisdictional audit.
- **2. AI Plan**: Automated CAF-aligned onboarding.
- **3. Govern AI**: Scoped least-privilege safety control plane.
- **4. Secure AI**: Real-time legal compliance audit (GDPR, CCPA, etc.).
- **5. Manage AI**: SRE-driven operational excellence and safety SLOs.

### 🏛️ Executive Command Center
- **Analytics**: Strategic Plotly-powered risk heatmaps and integrity matrices.
- **Review (HITL)**: Manual quarantine overrides and strategic exceptions.
- **Security**: Mandatory X-API-KEY handshake for all nodes.

## 📂 Capability Documentation
- [Capability: Jurisdictional Audit](capabilities/JURISDICTIONAL_AUDIT.md)
- [Capability: CAF Onboarding](capabilities/CAF_ONBOARDING.md)
- [Capability: Crypto-Agility](capabilities/CRYPTO_AGILITY.md)
- [Capability: Intelligent Safety](capabilities/LLM_SAFETY.md)
- [Capability: HITL Oversight](capabilities/HITL_REVIEW.md)

## 🗺️ Roadmaps
- [Roadmap: Education & Child Safety Pack](../blueprints/roadmap.md) — in flight
- [Roadmap: Live Governance Demo & Gap Hardening](../blueprints/roadmap-demo-and-gaps.md) — A+C tutor demo + closing the "Honest Take" gaps

## 📍 System Touchpoints
Agents should map their integration to the following `@touchpoint` locations in the codebase:
- `hub-decision`: Main evaluation loop in `aogi/ecosystem_hub.py`.
- `caf-onboarding`: Registry persistence in `aogi/ecosystem_hub.py`.
- `security-handshake`: API Key validation middleware.
- `llm-safety-scan`: Content safety NLP audit.
- `pii-redaction`: GDPR minimization rules in OPA.
- `quantum-rotation`: Algorithm agility in `aogi/crypto_engine.py`.
- `hitl-release`: Manual intervention endpoint for human rescue.
