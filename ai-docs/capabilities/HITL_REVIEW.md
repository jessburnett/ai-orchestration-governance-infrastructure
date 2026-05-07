# Capability: HITL Review

## 🤖 Description
Allows for **Human-in-the-Loop (HITL)** oversight of the autonomous fleet. Authorized human reviewers can inspect quarantined agents and grant **Strategic Exceptions** to persistently restore them to active status.

## 🛠️ Usage
Accessed via the `/review/release` endpoint.

### Required Context:
- `agent_name`: The asset to be released.
- `reviewer_note`: A required audit note justifying the exception (e.g., "Verified false positive").

## ⚖️ Strategic Integrity
Every manual intervention is recorded as a `human_intervention` signal in the telemetry stream, ensuring a permanent, auditable record of all human overrides.

## 🔗 Implementation
See `@touchpoint hitl-review-release` in `ecosystem_hub.py`.
