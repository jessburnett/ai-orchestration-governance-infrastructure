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

## ⚖️ Code of Conduct & CLA
Most contributions require you to agree to a Contributor License Agreement (CLA). For details, visit https://cla.opensource.microsoft.com.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com).
