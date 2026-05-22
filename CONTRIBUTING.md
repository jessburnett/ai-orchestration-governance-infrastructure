# Contributing to AOGI

This project welcomes contributions and suggestions. We follow the **Microsoft Open Source Standard** and the **AFDocs Elite Standard** for agent-friendly infrastructure.

## 🤖 Agent-Friendly Optimization (AXO)
All contributions must be optimized for AI agents following the [AFDocs](https://afdocs.dev) standard:
1.  **llms.txt**: Register new files and capabilities in the root `llms.txt` manifest.
2.  **Metadata Tags**: Include `<!-- agent-context: ... -->` tags in all new Markdown files.
3.  **URL Stability**: Do not break existing documentation URLs; use redirects if necessary.
4.  **Markdown First**: Ensure documentation remains readable in raw Markdown (avoid complex HTML/JS in docs).

## 🛡️ Strategic Testing
Every pull request must include updated tests in `tests/test_governance.py` covering:
- Jurisdictional compliance.
- Security handshakes.
- Intelligent safety scores.

## 🧭 Two-Repo Workflow (Sandbox → Upstream)

AOGI is the **sandbox** for the Microsoft Agent Governance Toolkit, vendored as a Git
submodule under `toolkit/`. Two lanes, decided by which folder a file lives in:

- **Lane A — AOGI work** (anything *outside* `toolkit/`: Rego, infra, docs, research):
  commit in this repo, push to the AOGI remote. Stays here. Never goes to Microsoft.
- **Lane B — toolkit work** (anything *inside* `toolkit/`): commit on your sandbox branch and
  push to your fork for backup. When a slice is ready for Microsoft, start a **fresh branch off
  freshly fetched `upstream/main`**, bring over only the scoped files for one topic, and
  prepare the PR.

**🔒 Upstream PR authority — maintainer only.** Only the maintainer (**Jessica Burnett**) opens
or submits pull requests to `microsoft/agent-governance-toolkit`. Contributors and AI agents
prepare scoped branches and drafts; they do **not** submit upstream PRs.

**Commit hygiene:** small, atomic commits that make sense — one concern each; one topic per PR;
upstream PR branches always start off freshly fetched `upstream/main` (never the sandbox branch).

## ⚖️ Code of Conduct & CLA
Most contributions require you to agree to a Contributor License Agreement (CLA). For details, visit https://cla.opensource.microsoft.com.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com).
