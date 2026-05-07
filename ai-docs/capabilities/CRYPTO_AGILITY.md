# Capability: Crypto Agility

## 🤖 Description
Provides agents with the ability to use modular cryptographic algorithms for signing and hashing. The infrastructure supports on-the-fly algorithm rotation (e.g., migrating from SHA-256 to Post-Quantum algorithms).

## 🛠️ Usage
Metadata in `/evaluate` or `/record` calls should specify:
- `crypto_alg`: The hashing algorithm used (e.g., `sha512`).
- `crypto_sig_alg`: The signature algorithm used (e.g., `hmac_sha256`).

## 🛡️ Policy Enforcement
The OPA engine verifies that the requested algorithm is in the **Approved Suite**. High-risk agents are automatically blocked if they use legacy or "Quantum-Vulnerable" math.

## 🔗 Implementation
See `@touchpoint quantum-rotation` in `crypto_engine.py`.
