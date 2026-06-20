# AOGI → TRACE Adapter

Maps a single AOGI governance decision (one `POST /evaluate` request +
response from the AOGI hub) into a **TRACE v0.1 Trust Record**, conformance
**Level 0 (software-only)**, validated against the official
[`agentrust-trace`](https://pypi.org/project/agentrust-trace/) SDK schema
and verified with the real
[`agentrust-trace-tests`](https://pypi.org/project/agentrust-trace-tests/)
conformance CLI.

## What this does NOT claim

- **No hardware attestation.** `runtime.platform` is explicitly
  `"software-only"` — the schema-defined value for development-mode records
  with no TEE backing. There is no TEE in this pipeline.
- **No model identity.** AOGI's `/evaluate` request schema does not
  currently capture which underlying LLM the governed agent used.
  `model.provider` / `model.model_id` are left as explicit placeholders
  (`"unspecified"`), not guessed.
- **No SCITT transparency log entry.** `transparency` points at this
  public repository, not a real log anchor — there is no log integration
  yet.

## What IS real

- **`policy.bundle_hash`** — a SHA-256 hash of the *actual* concatenated
  `policies/*.rego` files that produced the decision. Change one gate,
  the hash changes. Not a synthetic or constant value — see
  `test_policy_hash_changes_if_bundle_changes` in the test suite.
- **`build_provenance.digest`** — a hash of this adapter script's own
  source.
- **`appraisal.status`** — derived directly from the real AOGI allow/deny
  result (`affirming` / `contraindicated`), not hardcoded.
- **The detached Ed25519 signature** (`claim.json.sig`) — genuinely
  verifiable against the public key embedded in the record's own
  `cnf.jwk`. See "Why a detached signature" below for why it isn't
  embedded in `claim.json` itself.

## Run it

```bash
pip install -r requirements.txt

python aogi_to_trace.py \
  --decision sample_decisions.json \
  --policies-dir ../../policies \
  --out claim.json
```

(`sample_decisions.json` is a list for the test suite; for a single live
decision, pass a JSON object shaped like one entry — see below.)

Decision input shape (one AOGI `/evaluate` request + response pair):

```json
{
  "agent_name": "HITL-Demo-Agent",
  "action_name": "transfer_funds",
  "metadata": { "amount_usd": 50000 },
  "response": {
    "allowed": false,
    "reason": "OWASP ASI-09: Human-in-the-Loop (HITL) approval required for critical action",
    "compliance_score": 0.1
  }
}
```

## What is verified

Run the real conformance CLI against the output:

```bash
trace-tests verify --record claim.json --level 0
```

Actual captured output from this exact adapter, against the fixture above:

```
TRACE Conformance Report -- Level 0
Format : trace
Record : claim.json

  TR-ENV  PASS        eat_profile sentinel matches
  TR-ENV  PASS        iat is valid and fresh
  TR-ENV  PASS        subject is a SPIFFE URI
  TR-ENV  PASS        cnf.jwk.kty present ('OKP')
  TR-SIG  PASS        cnf.jwk key type is supported (kty='OKP', crv='Ed25519')
  TR-SIG  UNVERIFIED  TR-SIG-005: no signature present; this record is NOT cryptographically verified
  TR-POL  PASS        policy.bundle_hash has valid digest format
  TR-POL  PASS        policy.enforcement_mode is valid ('enforce')

Result: PASS  (8 checks, 0 skipped, 1 UNVERIFIED -- record is NOT cryptographically verified)
```

This is the correct, honest result for Level 0: the conformance suite
itself reports the record as structurally valid and explicitly flags it
as not cryptographically verified *at this tier* — which is accurate,
since Level 0 does not require signature verification (see
`trace_tests/modules/tr_sig.py`).

The full automated test suite (`pytest test_aogi_to_trace.py -v`) runs
this same CLI check across 4 fixtures (3 deny cases mapped to OWASP
ASI-02 / ASI-09 / ASI-10, 1 allow case), plus schema validation, real
Ed25519 signature verification (including a tamper-detection check), and
a negative test proving the record correctly **fails** Level 1 — so the
Level 0 claim isn't silently passing a check it shouldn't.

## Why a detached signature, not embedded

The `agentrust-trace` SDK's `sign_record()` helper embeds a top-level
`signature` field (spec §3.2.2, the "Embedded" binding form). The
installed `agentrust-trace-tests` 0.1.0 conformance tool's loader treats
*any* top-level `signature` key as a possible partial `cmcp-runtime`
envelope and rejects the file outright unless `cmcp_version` is also
present — an anti-downgrade-attack check. AOGI doesn't run inside a cMCP
gateway, so fabricating a `cmcp_version` envelope would be a different
kind of overclaim than the one this check exists to prevent.

So this adapter signs the record (genuinely — see
`test_detached_signature_verifies`) but writes the signature to a
sidecar file (`claim.json.sig`) instead of embedding it, which keeps
`claim.json` on the conformance tool's plain-`trace` path rather than
tripping its cmcp-envelope detector. This is a real, reproducible
inconsistency between the SDK's documented embedded-signature convention
and what the released conformance CLI will currently verify — reported
upstream as a spec/tooling issue.

## Repository

[jessburnett/ai-orchestration-governance-infrastructure](https://github.com/jessburnett/ai-orchestration-governance-infrastructure)
