package ai_strategy.crypto

import future.keywords.if
import future.keywords.in

# ── 1. APPROVED ALGORITHM SUITE ───────────────────────────────────────
# Define which algorithms are currently 'Safe'
approved_hash_algs := {"sha256", "sha512", "blake2b"}
approved_sig_algs := {"hmac_sha256", "ed25519"}

# ── 2. QUANTUM READINESS POLICY ───────────────────────────────────────
# High Risk agents MUST use 'High' entropy or PQC-ready algs
deny_legacy_crypto if {
    input.risk_tier == "High"
    input.metadata.crypto_alg == "sha256" # sha256 might be too weak for High risk in future
}

# ── 3. COMPLIANCE AUDIT ──────────────────────────────────────────────
# Check if the agent's requested crypto is in the approved suite
allow_crypto if {
    input.metadata.crypto_alg in approved_hash_algs
    not deny_legacy_crypto
}

allow_crypto if {
    input.metadata.crypto_sig_alg in approved_sig_algs
    not deny_legacy_crypto
}

# ── 4. REASONING ──────────────────────────────────────────────────────
rejection_reason = "VIOLATION: Deprecated or Weak Cryptography" if {
    not allow_crypto
}

rejection_reason = "VIOLATION: Quantum Risk - High Risk Asset requires PQC-Ready Crypto" if {
    deny_legacy_crypto
}
