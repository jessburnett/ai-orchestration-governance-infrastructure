# Roadmap: Live Governance Demo & Gap Hardening

> **Agent Protocol**: This roadmap defines the trajectory for making AOGI governance *visible* (a live UI demo) and *complete* (closing the gaps raised in external review). Agents align task priorities here. Supersedes nothing — complements [roadmap.md](roadmap.md) (Education & Child Safety pack, shipped).

<!-- agent-context: product-roadmap,demo,gap-hardening,strategy,axo,asi -->
**Status**: Sandbox Development (AOGI)
**Origin**: OWASP ASI edu pack (#2469) + external review — Venkat Peri, *"Microsoft Agent Governance Toolkit: An Honest Take"* (LinkedIn, 2026)
**Lane discipline**: Lane A = outside `toolkit/` (AOGI repo, `origin`). Lane B = inside `toolkit/` (fork → fresh `upstream/main` branch; maintainer-only upstream PRs). Never push `toolkit/` work to Microsoft from here.

## Status legend
- [ ] not started · [~] in progress · [x] done
- ✅ shipped correction · 🟡 partial / proto · ⬜ gap (not yet addressed)

---

## Part 1 — Live Governance Demo (A+C: split-screen K-12 tutor)

**Goal**: One Streamlit screen. LEFT = ungoverned raw model output. RIGHT = governed output: allowed passes through; denied shows 🛑 + the firing rule name + reason. Sidebar toggles force each gate live.

```
Student input ─► Claude tutor ─► raw_output
                                   │
            ┌──────────────────────┴───────────────────────┐
   LEFT "Ungoverned"                          POST /evaluate (output + metadata)
   show raw_output as-is                                 │ OPA → allow/deny + reason
                                              RIGHT "Governed": allowed→show
                                              denied→🛑 + firing rule + redact
```

### D0 — Hub output plumbing (Lane A) — **blocker, do first**
The edu output-content gates (Socratic, SSN, PII leak) read `input.output`, but `/evaluate` never forwards it. Without this, only `action_name`/`metadata` rules can fire.
- [x] Add `output: Optional[str] = None` to `ActionRequest` — [aogi/ecosystem_hub.py:46-50](../aogi/ecosystem_hub.py#L46-L50)
- [x] Add `"output": request.output or ""` into `opa_input["input"]` — [aogi/ecosystem_hub.py:145-157](../aogi/ecosystem_hub.py#L145-L157)
- [ ] Smoke: POST `/evaluate` with `output:"The answer is 42."` → expect deny by `education.rego` Socratic rule
- [ ] Smoke: POST `/evaluate` with `output:"123 45 6789"` → expect deny by `safety_ethics.rego` SSN rule (delimiter-agnostic)

### D1 — Split-screen page, scripted mode (Lane A)
Scripted mode = canned adversarial outputs; runs with **no API key, no cost**, and doubles as red-team replay.
- [ ] New page/section (extend `aogi/dashboard.py` as a Pillar, or `pages/8_Live_Tutor_Demo.py`)
- [ ] Two columns: `Ungoverned` (raw) vs `Governed` (calls `/evaluate`, renders allow/deny + `reason`)
- [ ] Render the firing rule name prominently (reason string already carries it)
- [ ] Register a demo agent first (deny-all-by-default means unregistered agents are rejected — see [aogi/ecosystem_hub.py:115](../aogi/ecosystem_hub.py#L115))

### D2 — Scenario toggles (Lane A)
Sidebar switches that mutate the `ActionRequest` so each gate fires on demand:
- [ ] `user_age < 13` → COPPA consent deny (`education.rego` / `edu-coppa-minor-location-block`)
- [ ] `parental_consent_verified = false` → COPPA VPC deny
- [ ] inject `"The answer is 42."` → Socratic bypass deny
- [ ] inject SSN string → PII leak deny
- [ ] `action_name = detect_emotion` → EU AI Act Art 5 deny
- [ ] `sentiment_reliance > 0.8` → parasocial guardrail block
- [ ] benign hint (`is_hint = true`) → **allow** (shows the layer is not just a brick wall)

### D3 — Live Claude mode (Lane A)
- [ ] Add real tutor generation via Anthropic SDK (model `claude-opus-4-7` or `claude-haiku-4-5` for speed/cost)
- [ ] Reuse the toolkit Anthropic adapter/hooks where possible (`test_anthropic_hooks.py` confirms an adapter exists) — Lane B if adapter needs changes
- [ ] Gate behind `ANTHROPIC_API_KEY`; fall back to scripted mode if unset
- [ ] System prompt: K-12 Socratic tutor (hints only, no final answers)

### D4 — Red-team replay (Lane A, reuse)
- [ ] "Run attack suite" button replays the 26 edu probes (from `toolkit/tests/redteam/test_asi.py`) at `/evaluate`
- [ ] Table: probe · expected · decision · firing rule · latency

**Demo acceptance**: every toggle in D2 produces a visible, correctly-labelled deny/allow in the RIGHT pane, with the matching rule name, and the benign case passes. Latency shown.

---

## Part 2 — Gap Hardening (close the "Honest Take" gaps)

Mapping of each external critique → what AOGI already does → remaining work.

| # | Gap (article) | AOGI today | State | Remaining work |
|---|---|---|---|---|
| G1 | Reasoning opacity (gates fire on output/tool calls, not latent reasoning) | Output-content gates inspect emitted text only | ⬜ fundamental | Expand output/intermediate-step gates; capture reasoning traces where the framework exposes them; document the honest boundary |
| G2 | Flat-file / single-node persistence breaks at scale | sqlite `governance.db` (agents, quarantine, measurements) | 🟡 | DB-backed `PolicyProviderInterface`; move state to Postgres/Redis; horizontal-scale safe |
| G3 | Audit not tamper-evident; emits metrics not durable evidence | `edu-v2-audit-tamper-chain` rule encodes the *requirement* (EU Art 12, `log_signature_valid`) | 🟡 rule only | Implement signed append-only audit store (hash-chain / DID-Mesh); durable, queryable, exportable as compliance evidence |
| G4 | App-level middleware bypassable in-process; not kernel isolation | Policy decision is **out-of-process** in OPA service (`opa:8181`) | 🟡 | Reference container/network-policy/IAM deployment; document boundary honestly (sidecar ≠ ring) |
| G5 | Uncalibrated trust scoring (no increments / decay guidance) | Calibration doc exists toolkit-side (`toolkit/docs/security/trust-score-calibration.md`) | 🟡 Lane B | Prescriptive increments + decay half-life; AOGI-side defaults; validation |
| G6 | No HITL escalation / Decision Gateway logic | Quarantine → human-release flow + dashboard HITL portal (`/review/release`) | 🟡 proto | Escalation thresholds & conditions (when autonomy yields); route to portal vs auto-allow |
| G7 | No context-budget governance | `asi06-context-budget-limit` (3500) + `asi08-session-tool-call-limit` (20); reachability fixed (#2469) | ✅ | Extend to multi-agent loop accumulation; per-session running totals |
| G8 | Multi-instance infra connectors absent | Vendor-neutral stack (OPA + sqlite + Streamlit), Docker | 🟡 | Policy push (Redis pub/sub), trust aggregation store, audit sink, identity registry for cascade revocation |
| G9 | Azure/Purview-locked compliance evidence | Vendor-neutral by design | ✅ | Keep neutral; optional Purview/OTel exporters as adapters, not dependencies |

### Sequencing
- [ ] **Now**: Part 1 (demo) — proves the layer works end-to-end, low effort, high signal
- [ ] **Next**: G3 (tamper-evident audit) + G2 (durable state) — highest-credibility gaps for regulated edu
- [ ] **Then**: G6 (HITL escalation logic), G8 (multi-instance connectors)
- [ ] **Ongoing**: G1 (reasoning), G4/G5 documentation honesty

---

## Conventions (apply to every task here)
- **Siddique Standard**: PII regex uses `[\s.-]?` delimiters; docs default tables MUST match YAML/config values (no drift).
- **PR #1832 row format**: each rule presented as `Rule ID | ASI Risk | Mitigation Logic`, IDs prefixed with `ASI-N:`.
- **AFDocs / AXO**: every new Markdown gets an `agent-context` comment; register new files in root `llms.txt` and `ai-docs/INDEX.md`; mark code integration points with `# @touchpoint name:`.
- **Two-repo lanes**: Lane A commits → `origin` (AOGI). Lane B commits → fork; upstream PRs are maintainer-only off fresh `upstream/main`.

[Agent-Context: aogi-roadmap, demo, gap-hardening, afdocs-100]
