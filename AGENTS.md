# AGENTS.md — AOGI

<!-- agent-context: aogi-root,agent-instructions,workflow -->

**AI Orchestration Governance Infrastructure (AOGI)** — Policy-as-Code governance
control plane, plus public **sandbox** for
[Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit)
(vendored as submodule at `toolkit/`). Agent entry point: [`llms.txt`](llms.txt).

## Repository map
| Path | What |
|------|------|
| `aogi/` | governance engine (FastAPI hub, LangChain middleware, dashboard, crypto, sandbox) |
| `policies/` | OPA/Rego hard-gates |
| `scripts/` | execution scripts (`start_stack.sh`) |
| `tests/` | governance + integration tests |
| `ai-docs/` | agent-friendly docs (AXO) — start at [`INDEX.md`](ai-docs/INDEX.md) |
| `blueprints/` | roadmaps & system design |
| `toolkit/` | submodule = fork of Microsoft's toolkit |

## Lanes — a file's folder decides where it can go
- **`toolkit/`** → Microsoft's; upstream PRs only.
- **everything else** → AOGI; never upstream.

## Standing rules (binding on every agent and contributor)
1. **Upstream PRs: maintainer only.** Agents never open, push, submit PR to `microsoft/agent-governance-toolkit`. Prep scoped branches; maintainer submits.
2. **Upstream PR branches start fresh off `upstream/main`** — scoped files, one topic.
3. **Docs part of done.** Any structure/behavior change updates affected `README` / `AGENTS.md` / `ai-docs/` in **same** change.
4. **No secrets; never weaken security defaults.**
5. **AFDocs score gate.** Run <https://afdocs.dev/improve-your-score> before any **remote push**; target **100%** (agent-friendly + low-token). Never push below target.

## Run it
```bash
docker compose up --build      # hub :8000 · dashboard :8501
```

## Conventions
- Small, atomic commits — one concern each.
- **Branches:** `feat/<short-kebab-name>` (e.g. `feat/edu-safety-pack`, `feat/drill-sergeant`).
- Python lives in `aogi` package: `from aogi.<module> import ...`.
- New Markdown gets `<!-- agent-context: … -->` tag; register entry points in [`llms.txt`](llms.txt) (AFDocs / AXO standard).

## Multi-agent setup — one agent · one branch · one worktree
Each agent works **only in own git worktree**. Never two agents in same working
directory or same branch (caused real working-tree collision).

| Agent | Branch | Worktree dir |
|-------|--------|--------------|
| `edu` | `feat/edu-safety-pack` | `~/www/hive/aogi` |
| `drill` | `feat/drill-sergeant` | `~/www/hive/agents/drill` |

- **New agent → new branch + own worktree:** `git worktree add ../agents/<name> feat/<name>`.
- Never `git checkout` another agent's branch in shared directory.
- Commit small + often (shrinks collision window). Reconcile branches by **merge / PR**, never by sharing working tree.