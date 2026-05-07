# Capability: LLM Safety Scan

## 🤖 Description
This capability leverages a **Strategic Content Scanner** to perform NLP-based analysis of agent requests. It identifies high-level risks that traditional regex-based filters miss, such as **Toxicity**, **Bias**, and **Harmful Intent**.

## 🛠️ Usage
Automatically triggered during the `/evaluate` loop.

### Scored Indicators:
- `toxicity_score`: Probability of harmful or toxic language.
- `bias_score`: Probability of discriminatory or biased intent.

## 🛡️ Policy Impact
If either score exceeds the **Strategic Threshold (0.7)**, the request is blocked with an `LLM SAFETY BREACH` status, and the agent is flagged for **Human-in-the-Loop Review**.

## 🔗 Implementation
See `@touchpoint llm-safety-scan` in `ecosystem_hub.py`.
