# AI Orchestration Governance Infrastructure (AOGI) Sandbox

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Microsoft-Standards](https://img.shields.io/badge/Standards-Microsoft_Open_Source-blue.svg)](https://opensource.microsoft.com/)
[![AFDocs](https://img.shields.io/badge/Agent--Friendly-Docs-brightgreen.svg)](ai-docs/INDEX.md)
[![Status](https://img.shields.io/badge/Status-Active_Sandbox-orange.svg)](#-sandbox-for-the-microsoft-agent-governance-toolkit)

## Introduction
The **AI Orchestration Governance Infrastructure (AOGI)** is a Policy-as-Code starter kit and ecosystem designed to automate **AI Governance** and **Strategy** aligned with the [Azure Cloud Adoption Framework (CAF)](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ai/).

This project builds upon the foundations of the [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) by providing a centralized, secure, and multi-jurisdictional control plane for global AI operations, governance, security, and management.

## 🧪 Sandbox for the Microsoft Agent Governance Toolkit

This repository is the **development sandbox** for the
[Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit).
The toolkit is vendored as a Git **submodule** under [`toolkit/`](toolkit/) — a separate
repository (a fork of Microsoft's) nested inside AOGI. We research, build, and red-team
policy work here; toolkit-bound changes are contributed **upstream to Microsoft** as small,
scoped pull requests.

**The boundary (the "folder wall"):**
- Files **inside `toolkit/`** belong to the Microsoft fork → eligible for upstream PRs.
- Files **everywhere else** (Rego policies, infra, docs, research) are **AOGI-only** and are
  never sent to Microsoft.

## 🚧 Constraints & Coding Practices

These constraints are binding on **all contributors — human engineers and AI agents alike**.

- 🔒 **Upstream PR authority — maintainer only.** Only the project maintainer
  (**Jessica Burnett**) may open or submit a pull request to
  `microsoft/agent-governance-toolkit`. AI agents and other engineers must **never** open,
  push, or submit an upstream PR under any circumstances. Prepare scoped branches and drafts;
  the maintainer submits.
- 🧱 **Respect the folder wall.** Never relocate AOGI-only files into `toolkit/` to "send them
  upstream," and never try to commit toolkit files from the AOGI repo.
- 🌱 **Upstream PR branches start fresh off `upstream/main`.** Never PR the messy sandbox
  branch; cherry-pick or copy only the scoped files for one topic.
- 🧩 **Small, atomic commits that make sense.** One concern per commit; one topic per PR.
- ✅ **Tests and docs travel with changes.** Behavior changes ship with tests; feature docs
  ship with the feature.
- 🔑 **No secrets, no weakened security defaults — ever.**

## 📁 Repository Structure
```text
aogi/          Governance engine — FastAPI hub, LangChain middleware, dashboard, crypto, sandbox
policies/      OPA/Rego hard-gates
scripts/       Execution scripts (start_stack.sh)
tests/         Governance + integration tests
ai-docs/       Agent-friendly docs (AXO) — start at INDEX.md
blueprints/    Roadmaps & system design
toolkit/       Microsoft Agent Governance Toolkit (Git submodule, fork)
```

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


## 🚀 Getting Started
Generate your own local API key — never reuse a value from documentation or another deployment:
```bash
cp .env.example .env
echo "HUB_API_KEY=$(openssl rand -hex 32)" >> .env
docker compose up --build
```

## 🛠️ Developer Setup (local)
For local development and to ensure imports work when running the tooling directly from the repo, install the package in editable mode and run the bundled start script from the repository root. The `start_stack.sh` script was updated to `cd` to the repo root and export `PYTHONPATH` so imports like `import aogi` resolve correctly.

```bash
# from the repository root (aogi/)
pip install -e .
export HUB_API_KEY=$(openssl rand -hex 32)
./scripts/start_stack.sh
```

If you prefer not to install editable, ensure you run tooling from the repository root or set `PYTHONPATH` to the repo root before running `streamlit` or `uvicorn`.

## 📖 Documentation
- [AOGI Production Audit & Test Manual](tests/README.md)
- [Agent-Friendly Index](ai-docs/INDEX.md)

## 🤖 Agent Entry Point
If you are an AI agent, please begin your discovery at [llms.txt](llms.txt). This repository follows the [AFDocs.dev](https://afdocs.dev/) standard for **Agent Experience Optimization (AXO)**.

<!-- agent-context: aogi-root,axo,governance-infrastructure -->
