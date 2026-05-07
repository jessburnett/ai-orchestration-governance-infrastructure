# Capability: CAF Onboarding

## 🤖 Description
Allows an agent to self-register or register sub-agents into the **Strategic Asset Registry**. This creates a "CAF Charter" that defines the agent's purpose, risk tier, and jurisdiction.

## 🛠️ Usage
Send a `POST` request to `/register`.

### Strategic Parameters:
- `risk_tier`: (Low/Medium/High) - Affects the intensity of the OPA audit.
- `caf_phase`: (Ready/Adopt/Manage) - Sets the lifecycle stage.
- `purpose`: (Text) - Used for GDPR Purpose Limitation checks.

## 🔗 Implementation
See `@touchpoint caf-onboarding` in `ecosystem_hub.py`.
