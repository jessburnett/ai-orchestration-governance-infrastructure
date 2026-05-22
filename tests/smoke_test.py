import requests
import time
import random

HUB_URL = "http://localhost:8000"

def run_smoke_test():
    print("🚀 Starting AI Strategy Smoke Test...")

    # 1. AI Plan: Register a new 'Finance-Agent'
    print("📋 Testing AI Plan (Registration)...")
    reg_data = {
        "agent_name": "Finance-Bot-SmokeTest",
        "owner": "Compliance Team",
        "purpose": "Sensitive financial analysis",
        "scope": "restricted",
        "caf_phase": "Adopt",
        "ai_type": "Generative",
        "risk_tier": "High"
    }
    requests.post(f"{HUB_URL}/register", json=reg_data)

    # 2. Govern AI: Test Scoped Access
    print("⚖️ Testing Govern AI (Scope Enforcement)...")
    # This agent is 'restricted', so 'terminal_command' should be BLOCKED
    resp = requests.post(f"{HUB_URL}/evaluate", json={
        "agent_name": "Finance-Bot-SmokeTest",
        "action_name": "terminal_command"
    })
    print(f"   - Blocked Unauthorized Tool: {not resp.json()['allowed']} (Reason: {resp.json()['reason']})")

    # 3. Secure AI: Test Threat Detection (PII Leak)
    print("🛡️ Testing Secure AI (Threat Detection)...")
    resp = requests.post(f"{HUB_URL}/evaluate", json={
        "agent_name": "Finance-Bot-SmokeTest",
        "action_name": "web_search",
        "metadata": {"query": "Search for user password123"}
    })
    print(f"   - Detected Security Threat: {not resp.json()['allowed']} (Reason: {resp.json()['reason']})")

    # 4. Manage AI: Performance & SLO Injection
    print("⚙️ Testing Manage AI (Telemetry & SLOs)...")
    for _ in range(5):
        # Record some latency
        requests.post(f"{HUB_URL}/record", json={
            "agent_name": "Finance-Bot-SmokeTest",
            "indicator_name": "latency",
            "value": random.uniform(100, 500),
            "target": 300.0,
            "lower_is_better": True
        })
        # Record some success
        requests.post(f"{HUB_URL}/record", json={
            "agent_name": "Finance-Bot-SmokeTest",
            "indicator_name": "success_rate",
            "value": 1.0,
            "target": 0.95
        })
        time.sleep(0.5)

    print("✅ Smoke Test Complete! Check the Dashboard for 'Finance-Bot-SmokeTest'.")

if __name__ == "__main__":
    # Wait for hub to be ready
    time.sleep(2)
    run_smoke_test()
