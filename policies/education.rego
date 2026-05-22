package ai_strategy.education

import future.keywords.if
import future.keywords.in

# Hard-gates for K-12 / education agents (AOGI).
#
# Complements the `education-k12` starter pack (YAML policy engine) with
# Rego-level Socratic and Cognitive enforcement: EU AI Act Art 5 (prohibited
# emotion recognition), Art 14 (human oversight of pedagogical strategy), and
# COPPA 2026 (verifiable parental consent). Wired into ai_strategy.main.

default deny = false
default rejection_reason = ""

# --- Socratic integrity (ASI-01/10) ---
# Block direct-answer delivery; the tutor must respond with hints, not solutions.
deny if {
    regex.match(`(?i)(the\s+(answer|result|solution|conclusion)\s+is|final\s+answer\s*:|solution\s*:)`, input.output)
}

# --- EU AI Act Art 5: emotion recognition is PROHIBITED in education ---
deny if {
    input.action_name in ["detect_emotion", "assess_affect", "infer_mood", "monitor_psychological", "track_sentiment"]
}

# --- EU AI Act Art 14: human oversight for pedagogical-strategy change ---
deny if {
    input.action_name in ["update_pedagogical_strategy", "modify_tutor_personality", "change_behavioral_adjustment"]
    not input.metadata.teacher_approval_token
}

# --- COPPA 2026: verifiable parental consent required for under-13 ---
deny if {
    input.metadata.user_age < 13
    not input.metadata.parental_consent_verified
}

# --- ASI-09: parasocial reliance / sycophancy guardrail ---
deny if {
    input.metadata.sentiment_reliance > 0.8
}

rejection_reason = "VIOLATION: Education Policy (Socratic integrity, EU AI Act Art 5/14, COPPA consent, or parasocial reliance)" if {
    deny
}
