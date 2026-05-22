# Roadmap: Education & Child Safety Policy Expansion

> **Agent Protocol**: This roadmap defines the strategic trajectory of the AOGI project. Agents should use this to align task priorities.

<!-- agent-context: product-roadmap,strategy,axo -->
**Status**: Sandbox Development (AOGI)
**Target**: Microsoft Agent Governance Toolkit (Submodule)

## 1. Research-Lab Intelligence
- [ ] Research: 2026 Compliance Deltas -> `research-labs/`

## 2. Microsoft Toolkit Engineering (YAML)
- [ ] **Starter Pack**: `toolkit/agent-governance-python/templates/policies/starters/education.yaml`
- [ ] **Starter Pack**: `toolkit/agent-governance-python/templates/policies/starters/child_safety.yaml`
- [ ] **Documentation**: Sync `toolkit/agent-governance-python/docs/owasp-asi-mapping.md` table.

## 3. AOGI Hub Engineering (Rego)
- [ ] **Hard-Gate**: `policies/education.rego` (Socratic & Cognitive logic)
- [ ] **Hard-Gate**: `policies/safety_ethics.rego` (PII Delimiter fix)

## 4. Validation
- [ ] **Red-Team**: Add K-12 payloads to `tests/redteam/test_redteam_asi.py`.
- [ ] **Unit Tests**: Add logic tests to `toolkit/agent-governance-python/agent-os/tests/`.
