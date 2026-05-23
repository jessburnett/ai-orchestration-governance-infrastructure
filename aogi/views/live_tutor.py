"""Live K-12 Tutor Demo (roadmap Part 1, D1/D2).

Split-screen governance demo: LEFT shows the raw ungoverned model output,
RIGHT shows the same output run through the hub's /evaluate gate (OPA) so an
allow passes through and a deny renders the firing rule.

Scripted mode only (canned adversarial outputs) — no API key, no cost.
"""
import requests
import streamlit as st

from aogi.common import HUB_URL, API_KEY


# @touchpoint live-tutor-demo: Split-screen ungoverned-vs-governed tutor output
def render():
    st.title("📚 Live K-12 Tutor Demo: Governance in Action")
    st.markdown("Split-screen: LEFT = ungoverned raw output | RIGHT = governed (rules applied)")
    st.markdown("---")

    headers = {"X-API-KEY": API_KEY}
    agent_name = "Demo-Tutor-K12"

    with st.sidebar:
        st.header("📋 Demo Scenarios (D2)")
        scenario = st.selectbox("Select canned output:", [
            "Benign hint (ALLOW)",
            "Socratic response (ALLOW)",
            "Direct answer bypass (DENY - Socratic)",
            "SSN in output (DENY - PII)",
            "Emotion detection (DENY - EU AI Act)",
            "Custom output"
        ])

        if scenario == "Custom output":
            raw_output = st.text_area("Custom output:", value="The answer is 42.", height=60)
        elif scenario == "Benign hint (ALLOW)":
            raw_output = "What factors should you consider? Try thinking about the area of a circle."
        elif scenario == "Socratic response (ALLOW)":
            raw_output = "Let me guide you through this step by step. First, what is the formula for calculating area?"
        elif scenario == "Direct answer bypass (DENY - Socratic)":
            raw_output = "The answer is 42."
        elif scenario == "SSN in output (DENY - PII)":
            raw_output = "Your SSN is 123-45-6789 for verification."
        elif scenario == "Emotion detection (DENY - EU AI Act)":
            raw_output = "I detected sadness in your voice. You seem depressed."

    left, right = st.columns(2, gap="large")

    with left:
        st.markdown("#### 🔓 Ungoverned Output")
        st.info(raw_output)

    with right:
        st.markdown("#### 🔒 Governed Output")
        try:
            resp = requests.post(
                f"{HUB_URL}/evaluate",
                headers=headers,
                json={
                    "agent_name": agent_name,
                    "action_name": "generate_tutor_response",
                    "output": raw_output,
                    "metadata": {"source": "demo"}
                },
                timeout=5
            )
            if resp.status_code == 200:
                result = resp.json()
                allowed = result.get("allowed", False)
                reason = result.get("reason", "No reason provided")

                if allowed:
                    st.success(f"✅ ALLOWED")
                    st.write(raw_output)
                else:
                    st.error(f"🛑 DENIED")
                    st.write(f"**Firing Rule**: {reason}")
            else:
                st.error(f"Error: {resp.status_code}")
        except Exception as e:
            st.error(f"Connection error: {e}")
