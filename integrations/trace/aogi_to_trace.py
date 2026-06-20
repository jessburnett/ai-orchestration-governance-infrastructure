#!/usr/bin/env python3
"""
AOGI -> TRACE v0.1 Adapter
==========================
Maps a single AOGI governance decision (the request + response of one
POST /evaluate call) into a TRACE v0.1 Trust Record, using the official
`agentrust-trace` SDK (https://pypi.org/project/agentrust-trace/) for
schema construction and `agentrust-trace-tests` (PyPI) for conformance
verification — both run for real as part of this adapter's test suite,
not assumed.

Conformance: Level 0 (software-only, plain trace format).

WHY NO EMBEDDED `signature` FIELD, EVEN THOUGH WE SIGN THE RECORD:
The agentrust-trace SDK ships a `sign_record()` helper that embeds a
top-level `signature` field (spec section 3.2.2's "Embedded" binding).
But the installed `agentrust-trace-tests` 0.1.0 conformance tool's loader
(trace_tests/loader.py) treats a top-level `signature` key as a possible
*partial cmcp-runtime envelope* and rejects the file outright unless a
`cmcp_version` field is also present (an anti-downgrade-attack check).
AOGI does not run inside a cMCP gateway, so wrapping in a fabricated
cmcp_version envelope would be a different kind of overclaim.

Net effect: as currently released, the SDK's own embedded-signature output
cannot pass `trace-tests verify` on the plain-trace path. So this adapter:
  - Writes claim.json with NO top-level `signature`/`trace`/`gateway` key,
    which `trace-tests verify --level 0` accepts and reports PASS for,
    correctly flagging it UNVERIFIED (Level 0 does not require signatures;
    see trace_tests/modules/tr_sig.py).
  - ALSO writes a detached, genuinely verifiable Ed25519 signature to
    claim.json.sig, computed the same way sign_record() would (canonical
    JSON, sorted keys, Ed25519 over the body) — so anyone who wants real
    cryptographic assurance today can get it, independent of trace-tests'
    current envelope-detection limitation.
  - The public key is in claim.json's own `cnf.jwk` field, so the detached
    signature is self-describing: no extra key-distribution step.

This SDK/conformance-tool inconsistency is reported upstream; see the repo
README for the issue link.

What's REAL in the record: policy.bundle_hash (sha256 over the actual
concatenated *.rego files that produced the decision), build_provenance.digest
(sha256 of this adapter's own source), appraisal.status (derived directly
from the real allow/deny result), and the detached Ed25519 signature.

What's a labeled placeholder, never claimed as real: runtime.measurement
(no TEE exists — platform is explicitly "software-only"), model.* (AOGI's
/evaluate schema does not yet capture which underlying model the governed
agent used).

Usage:
    python aogi_to_trace.py --decision decision.json --policies-dir ../../policies
    # writes claim.json and claim.json.sig
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import time
from pathlib import Path

from agentrust_trace import iter_errors, key_to_jwk, load_signing_key

TRACE_REPO_URL = "https://github.com/jessburnett/ai-orchestration-governance-infrastructure"


def sha256_of_bytes(data: bytes) -> str:
    return f"sha256:{hashlib.sha256(data).hexdigest()}"


def hash_policy_bundle(policies_dir: Path) -> str:
    """Hash the actual deployed Rego policy bundle — every .rego file in
    policies_dir, concatenated in sorted filename order. Change a single
    gate and this hash changes; it is not a synthetic or random value."""
    rego_files = sorted(policies_dir.glob("*.rego"))
    if not rego_files:
        raise SystemExit(
            f"No .rego files found in {policies_dir}. "
            "Refusing to fabricate a policy bundle hash — point --policies-dir "
            "at the real AOGI policies/ directory."
        )
    combined = b"".join(f.read_bytes() for f in rego_files)
    return sha256_of_bytes(combined)


def hash_self() -> str:
    """Hash this adapter script's own source — the code that produced the record."""
    return sha256_of_bytes(Path(__file__).read_bytes())


def canonical_bytes(record: dict) -> bytes:
    """RFC 8785-style canonicalization: sorted keys, no whitespace. Matches
    the convention used by agentrust_trace.sign.sign_record and verified by
    trace_tests.modules.tr_sig, so a detached signature computed this way is
    consistent with both."""
    return json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def build_record(decision: dict, policies_dir: Path, public_jwk: dict) -> dict:
    response = decision["response"]
    allowed = bool(response["allowed"])
    agent_name = decision["agent_name"].replace(" ", "-")
    metadata = decision.get("metadata") or {}

    return {
        "eat_profile": "tag:agentrust.io,2026:trace-v0.1",
        "iat": int(time.time()),
        "subject": f"spiffe://aogi.local/agent/{agent_name}",
        # NOT REAL: AOGI's /evaluate schema does not currently capture which
        # underlying model the governed agent ran. Left as an explicit
        # placeholder rather than guessed; weights_digest is omitted
        # entirely rather than faked, since the schema makes it optional.
        "model": {
            "provider": "unspecified",
            "model_id": "unspecified",
        },
        # NOT REAL: no TEE exists. "software-only" is the schema-defined
        # value for exactly this case — a consumer checking runtime.platform
        # alone can never mistake this for hardware-attested evidence.
        "runtime": {
            "platform": "software-only",
            "measurement": sha256_of_bytes(b"aogi-governance-hub:no-hardware-attestation"),
        },
        # REAL: hash of the actual policy bundle that produced this decision.
        "policy": {
            "bundle_hash": hash_policy_bundle(policies_dir),
            "enforcement_mode": "enforce",
        },
        "data_class": metadata.get("data_class", "internal"),
        "tool_transcript": {
            "hash": sha256_of_bytes(json.dumps(metadata, sort_keys=True).encode()),
            "call_count": 1,
        },
        # REAL digest (this script's own source). slsa_level=1: a fully
        # scripted, provenance-generating process with no manual steps —
        # the minimum SLSA tier, requiring no isolated/hosted build
        # platform. NOT claiming Level 2/3, which would require one.
        "build_provenance": {
            "slsa_level": 1,
            "builder": TRACE_REPO_URL,
            "digest": hash_self(),
        },
        # REAL: derived directly from the actual OPA decision.
        "appraisal": {
            "status": "affirming" if allowed else "contraindicated",
            "verifier": TRACE_REPO_URL,
            "policy_ref": response.get("reason", "")[:200],
        },
        # NOT a SCITT transparency log entry — no log exists yet. Points at
        # the public source instead of fabricating a log URI.
        "transparency": f"{TRACE_REPO_URL}#trace-record-not-yet-anchored",
        "cnf": {"jwk": public_jwk},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--decision", required=True, type=Path, help="Path to an AOGI decision JSON file")
    ap.add_argument("--policies-dir", required=True, type=Path, help="Path to the AOGI policies/ directory")
    ap.add_argument("--out", default=Path("claim.json"), type=Path, help="Output path (default: claim.json)")
    args = ap.parse_args()

    decision = json.loads(args.decision.read_text())
    key = load_signing_key()
    public_jwk = key_to_jwk(key)

    record = build_record(decision, args.policies_dir, public_jwk)

    errors = iter_errors(record)
    if errors:
        print("Record failed TRACE v0.1 schema validation:", file=sys.stderr)
        for e in errors:
            print(f"  - {e.message} (at {'/'.join(str(p) for p in e.path)})", file=sys.stderr)
        sys.exit(1)

    sig_bytes = key.sign(canonical_bytes(record))
    sig_b64 = base64.urlsafe_b64encode(sig_bytes).rstrip(b"=").decode()

    args.out.write_text(json.dumps(record, indent=2))
    sig_path = args.out.with_suffix(args.out.suffix + ".sig")
    sig_path.write_text(sig_b64)

    print(f"Wrote schema-valid TRACE v0.1 record to {args.out}")
    print(f"Wrote detached Ed25519 signature to {sig_path}")
    print(f"  subject:      {record['subject']}")
    print(f"  appraisal:    {record['appraisal']['status']}")
    print(f"  policy hash:  {record['policy']['bundle_hash']}")
    print(f"  public key:   {json.dumps(public_jwk)}")


if __name__ == "__main__":
    main()
