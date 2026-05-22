# AGENTS.md — AOGI

<!-- agent-context: aogi-root,agent-instructions,workflow -->

**AI Orchestration Governance Infrastructure (AOGI)** — a Policy-as-Code governance
control plane, and the public **sandbox** for the
[Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)
(vendored as a submodule at `toolkit/`). Agent entry point: [`llms.txt`](llms.txt).

## Repository map
| Path | What |
|------|------|
| `aogi/` | the governance engine (FastAPI hub, LangChain middleware, dashboard, crypto, sandbox) |
| `policies/` | OPA/Rego hard-gates |
| `scripts/` | execution scripts (`start_stack.sh`) |
| `tests/` | governance + integration tests |
| `ai-docs/` | agent-friendly docs (AXO) — start at [`INDEX.md`](ai-docs/INDEX.md) |
| `blueprints/` | roadmaps & system design |
| `toolkit/` | submodule = fork of Microsoft's toolkit |

## Lanes — a file's folder decides where it can go
- **`toolkit/`** → Microsoft's; eligible for upstream PRs only.
- **everything else** → AOGI; never sent upstream.

## Standing rules (binding on every agent and contributor)
1. **Upstream PRs: maintainer only.** Agents never open, push, or submit a PR to `microsoft/agent-governance-toolkit`. Prepare scoped branches; the maintainer submits.
2. **Upstream PR branches start fresh off `upstream/main`** — scoped files, one topic.
3. **Docs are part of done.** Any change to structure or behavior updates the affected `README` / `AGENTS.md` / `ai-docs/` in the **same** change.
4. **No secrets; never weaken security defaults.**
5. **AFDocs score gate.** Run <https://afdocs.dev/improve-your-score> before any **remote push**; target **100%** (agent-friendly + low-token). Never push below target.

## Run it
```bash
docker compose up --build      # hub :8000 · dashboard :8501
```

## Conventions
- Small, atomic commits — one concern each.
- Python lives in the `aogi` package: `from aogi.<module> import ...`.
- New Markdown gets an `<!-- agent-context: … -->` tag; register entry points in [`llms.txt`](llms.txt) (AFDocs / AXO standard).
