# AI Orchestration Governance Infrastructure (AOGI)

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Microsoft-Standards](https://img.shields.io/badge/Standards-Microsoft_Open_Source-blue.svg)](https://opensource.microsoft.com/)
[![AFDocs](https://img.shields.io/badge/Agent--Friendly-Docs-brightgreen.svg)](ai-docs/INDEX.md)
[![Quality-Harden](https://img.shields.io/badge/Quality-Production_Ready-gold.svg)](#high-quality-hardening)

## Introduction
The **AI Orchestration Governance Infrastructure (AOGI)** is a production-grade starter kit and Policy-as-Code ecosystem designed to automate **AI Governance** and **Strategy** aligned with the [Azure Cloud Adoption Framework (CAF)](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/).

This project builds upon the foundations of the [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) by providing a centralized, secure, and multi-jurisdictional control plane for global AI operations, governance, security, and management.

## 🌟 The AOGI Strategic Lifecycle
The core UI is organized into a **5-Pillar CAF Wizard** for active asset management, supported by a **Command Center** for executive oversight.

### 🏗️ The 5-Pillar Wizard (CAF Lifecycle)
1.  **AI Strategy**: Executive oversight and jurisdictional certification.
2.  **AI Plan**: Automated onboarding using the CAF Decision Tree.
3.  **Govern AI**: Active control plane with scoped least-privilege access.
4.  **Secure AI**: Real-time threat intelligence (PII, GDPR, CPA, CCPA).
5.  **Manage AI**: Operational excellence via SLOs and an automated Kill-Switch.

### 🏛️ The Command Center (Executive Oversight)
- **📊 Strategic Analytics**: Interactive Plotly-powered executive risk heatmaps (Sidebar).
- **🏛️ HITL Review Portal**: Human-in-the-Loop exception and quarantine management (Sidebar).
- **🛠️ System Debug Console**: Real-time connectivity and security handshake audit (Sidebar).

## ⚖️ Built-in Compliance Bundles
- 🇪🇺 **EU GDPR**: Data minimization, purpose limitation, and cross-border transfer.
- 🌉 **California CCPA/CPRA**: Mandatory AI disclosure and user opt-out.
- 🏔️ **Colorado CPA**: Strict PII guardrails for high-risk assets.
- 🔐 **Crypto Agility**: Post-Quantum ready algorithm rotation via Policy-as-Code.

## 💎 High-Quality Hardening
- **Persistent Strategic Registry**: Powered by SQLite for durable CAF charters.
- **Enterprise Security**: Mandatory API Key authentication (X-API-KEY) for all endpoints.
- **Resilient Hub Architecture**: Automatic retry loops for OPA engine connectivity.
- **Intelligent Safety**: LLM-powered toxicity and bias detection.

## 🚀 Getting Started
Ensure your API Key is set in the environment:
```bash
export HUB_API_KEY="agt-secret-key-2024"
docker-compose up --build
```

## 📖 Documentation
- [AOGI Production Audit & Test Manual](tests/README.md)
- [Agent-Friendly Index](ai-docs/INDEX.md)

## 🤖 Agent Entry Point
If you are an AI agent, please begin your discovery at [ai-docs/INDEX.md](ai-docs/INDEX.md). This repository follows the [AFDocs.dev](https://afdocs.dev/) standard for agent-friendly documentation.
