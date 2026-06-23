# AOGI — AI Orchestration Governance Infrastructure

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Microsoft Standards](https://img.shields.io/badge/Standards-Microsoft_Open_Source-blue.svg)](https://opensource.microsoft.com/)
[![Agent Friendly](https://img.shields.io/badge/Agent--Friendly-AXO-brightgreen.svg)](ai-docs/INDEX.md)
[![Status](https://img.shields.io/badge/Status-Active_Sandbox-orange.svg)](#sandbox)

AOGI is a **policy-as-code sandbox** for researching, building, and red-teaming AI governance controls. It produces upstream contributions to the [Microsoft Agent Governance Toolkit (AGT)](https://github.com/microsoft/agent-governance-toolkit).

**This is not a production system.** It is a research and contribution environment. Do not represent it as deployable governance infrastructure.

---

## What's here

| Path | Contents |
|------|----------|
| `policies/` | OPA/Rego governance policies — EU AI Act finance domain, healthcare, SaaS |
| `data/` | Governance configuration loaded by policies — allowlists, risk classifications, egress patterns |
| `examples/` | Evaluators and red-team tooling wiring policies to AGT and agentrust-trace |
| `tests/` | Policy unit tests and integration tests |
| `toolkit/` | Microsoft AGT (Git submodule — fork of `microsoft/agent-governance-toolkit`) |
| `ai-docs/` | Agent-readable documentation (AXO format) — start at [INDEX.md](ai-docs/INDEX.md) |
| `blueprints/` | Research notes and roadmap |
| `red-team/` | Adversarial red-team scripts and findings, mapped to OWASP Agentic Top 10 |
| `aogi/` | FastAPI governance hub, LangChain middleware, Streamlit dashboard |

---

## Upstream relationship

Research and red-team work happens in AOGI. Scoped, tested changes are contributed upstream as small, clean PRs to Microsoft AGT.

**The folder wall:**
- Files inside `toolkit/` belong to the Microsoft fork → eligible for upstream PRs
- Everything else is AOGI-only and never goes upstream directly

---

## Constraints

These apply to all contributors — human and AI alike.

- 🔒 **Upstream PR authority — maintainer only.** Only Jessica Burnett may open or submit a PR to `microsoft/agent-governance-toolkit`. AI agents must never open, push, or submit upstream PRs under any circumstances.
- 🧱 **Respect the folder wall.** Never move AOGI files into `toolkit/`.
- 🌱 **Upstream branches start fresh off `upstream/main`.** Never PR from the sandbox branch directly.
- 🧩 **One concern per commit, one topic per PR.**
- ✅ **Tests and docs travel with behavior changes.**
- 🔑 **No secrets, no weakened security defaults — ever.**

---

## Getting started

Generate a local API key — never reuse a value from documentation or another deployment:

```bash
cp .env.example .env
echo "HUB_API_KEY=$(openssl rand -hex 32)" >> .env
docker compose up --build
```

For local development without Docker:

```bash
pip install -e .
export HUB_API_KEY=$(openssl rand -hex 32)
./scripts/start_stack.sh
```

---

## Documentation

- [Agent-Friendly Index](ai-docs/INDEX.md)
- [Test and Audit Guide](tests/README.md)

---

## Agent entry point

AI agents: start at [llms.txt](llms.txt). This repository follows the [AFDocs.dev](https://afdocs.dev/) AXO standard for agent-readable documentation.

<!-- agent-context: aogi-sandbox,policy-as-code,opa,rego,agt,agentrust-trace,owasp-agentic-top-10,eu-ai-act,red-team,governance -->
