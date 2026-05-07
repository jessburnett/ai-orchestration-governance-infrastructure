# Contributing to AOGI

This project welcomes contributions and suggestions. We follow the **Microsoft Open Source Standard** and the **AFDocs Elite Standard** for agent-friendly infrastructure.

## 🤖 Agent-Friendly Documentation (AFDocs)
All new features and capabilities **must** be documented for AI agents:
1.  **Capability Docs**: Create a new `.md` file in `ai-docs/capabilities/` explaining the feature.
2.  **Touchpoints**: Add `@touchpoint <name>` tags to the relevant lines of code.
3.  **Index**: Register the new capability in `ai-docs/INDEX.md`.

## 🛡️ Strategic Testing
Every pull request must include updated tests in `tests/test_governance.py` covering:
- Jurisdictional compliance.
- Security handshakes.
- Intelligent safety scores.

## ⚖️ Code of Conduct & CLA
Most contributions require you to agree to a Contributor License Agreement (CLA). For details, visit https://cla.opensource.microsoft.com.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/). For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or contact [opencode@microsoft.com](mailto:opencode@microsoft.com).
