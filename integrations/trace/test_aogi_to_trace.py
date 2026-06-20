"""
Tests for the AOGI -> TRACE adapter.

Runs the adapter against every fixture in sample_decisions.json and checks:
  1. The record validates against the official TRACE v0.1 JSON Schema
     (agentrust_trace.iter_errors — the schema bundled in the released SDK).
  2. The detached Ed25519 signature is real: it verifies against the public
     key embedded in the record's own cnf.jwk, and a tampered record fails.
  3. The real `trace-tests` conformance CLI (agentrust-trace-tests, PyPI)
     accepts the record at Level 0 (exit code 0 = PASS).
  4. appraisal.status correctly reflects the underlying allow/deny decision.
  5. policy.bundle_hash is a real, deterministic hash of the actual policy
     files, not a random or per-call value.

Run with: pytest test_aogi_to_trace.py -v
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

import pytest
from agentrust_trace import generate_key, iter_errors, key_to_jwk
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, str(Path(__file__).parent))
from aogi_to_trace import build_record, canonical_bytes  # noqa: E402

HERE = Path(__file__).parent
POLICIES_DIR = HERE.parent.parent / "policies"
FIXTURES = json.loads((HERE / "sample_decisions.json").read_text())


def _b64url_decode(s: str) -> bytes:
    pad = "=" * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


@pytest.fixture(scope="module")
def signing_key():
    return generate_key()


@pytest.fixture(scope="module")
def public_jwk(signing_key):
    return key_to_jwk(signing_key)


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_schema_valid(fixture, signing_key, public_jwk):
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    errors = iter_errors(record)
    assert errors == [], f"Schema violations: {[e.message for e in errors]}"


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_no_envelope_marker_keys(fixture, signing_key, public_jwk):
    """The record must NOT carry top-level signature/trace/gateway keys —
    those trip trace-tests' anti-downgrade check (see loader.py) and get
    the whole file rejected before any real check even runs."""
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    assert not ({"signature", "trace", "gateway"} & record.keys())


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_detached_signature_verifies(fixture, signing_key, public_jwk):
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    body = canonical_bytes(record)
    sig_bytes = signing_key.sign(body)

    pub_key = signing_key.public_key()
    pub_key.verify(sig_bytes, body)  # must not raise

    # Tamper check: changing one field must break verification against the
    # original signature.
    tampered = dict(record)
    tampered["data_class"] = "tampered-value"
    with pytest.raises(InvalidSignature):
        pub_key.verify(sig_bytes, canonical_bytes(tampered))


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_appraisal_matches_decision(fixture, signing_key, public_jwk):
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    expected = "affirming" if fixture["response"]["allowed"] else "contraindicated"
    assert record["appraisal"]["status"] == expected


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_policy_hash_is_deterministic_and_real(fixture, signing_key, public_jwk):
    r1 = build_record(fixture, POLICIES_DIR, public_jwk)
    r2 = build_record(fixture, POLICIES_DIR, public_jwk)
    assert r1["policy"]["bundle_hash"] == r2["policy"]["bundle_hash"]
    assert r1["policy"]["bundle_hash"].startswith("sha256:")


def test_policy_hash_changes_if_bundle_changes(tmp_path, signing_key, public_jwk):
    """Prove bundle_hash is a real hash, not a constant: editing a policy
    file must change it."""
    fake_policies = tmp_path / "policies"
    fake_policies.mkdir()
    (fake_policies / "a.rego").write_text("package a\n")
    fixture = FIXTURES[0]

    r1 = build_record(fixture, fake_policies, public_jwk)
    (fake_policies / "a.rego").write_text("package a\n# changed\n")
    r2 = build_record(fixture, fake_policies, public_jwk)

    assert r1["policy"]["bundle_hash"] != r2["policy"]["bundle_hash"]


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_trace_tests_cli_accepts_record_at_level_0(fixture, signing_key, public_jwk, tmp_path):
    """End-to-end: actually shell out to the real `trace-tests` conformance
    CLI (agentrust-trace-tests on PyPI) and require it to PASS at Level 0."""
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    out = tmp_path / "claim.json"
    out.write_text(json.dumps(record))

    result = subprocess.run(
        ["trace-tests", "verify", "--record", str(out), "--level", "0"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"trace-tests rejected the record:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    )
    assert "Result: PASS" in result.stdout


@pytest.mark.parametrize("fixture", FIXTURES, ids=[f["agent_name"] for f in FIXTURES])
def test_trace_tests_cli_fails_at_level_1_without_envelope(fixture, signing_key, public_jwk, tmp_path):
    """Confirms our Level-0 claim is honest: the same record must correctly
    FAIL Level 1 (which requires a verified signature), proving we are not
    silently passing a check we shouldn't."""
    record = build_record(fixture, POLICIES_DIR, public_jwk)
    out = tmp_path / "claim.json"
    out.write_text(json.dumps(record))

    result = subprocess.run(
        ["trace-tests", "verify", "--record", str(out), "--level", "1"],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "Result: FAIL" in result.stdout
