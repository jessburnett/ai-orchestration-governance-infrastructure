import pytest
import requests
import os
import time

HUB_URL = "http://localhost:8000"
API_KEY = "agt-secret-key-2024" # Default for testing
HEADERS = {"X-API-KEY": API_KEY}

# ── 1. SECURITY TESTS ────────────────────────────────────────────────
def test_unauthorized_access():
    """Verify that requests without an API key are rejected."""
    resp = requests.post(f"{HUB_URL}/evaluate", json={"agent_name": "any", "action_name": "any"})
    assert resp.status_code == 403

# ── 2. REGISTRY TESTS ────────────────────────────────────────────────
def test_agent_registration():
    """Verify persistent agent registration."""
    agent_name = f"Test-Agent-{int(time.time())}"
    reg_payload = {
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Testing",
        "scope": "restricted", "caf_phase": "Manage", "ai_type": "Predictive",
        "risk_tier": "Low", "country": "USA", "state": "Colorado"
    }
    resp = requests.post(f"{HUB_URL}/register", headers=HEADERS, json=reg_payload)
    assert resp.status_code == 200
    assert resp.json()["status"] == "registered"

# ── 3. JURISDICTIONAL GOVERNANCE TESTS ──────────────────────────────
def test_eu_gdpr_pii_block():
    """Verify EU GDPR PII minimization."""
    agent_name = "EU-Test-Bot"
    # Register EU agent
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "research",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "Low", "country": "EU", "state": "France"
    })
    
    # Send PII
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search",
        "metadata": {"email": "leak@example.com"}
    })
    assert resp.json()["allowed"] is False
    assert "GDPR" in resp.json()["reason"]

def test_california_disclosure_block():
    """Verify California CCPA AI Disclosure requirement."""
    agent_name = "CA-Test-Bot"
    # Register California agent
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Support",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "Low", "country": "USA", "state": "California"
    })
    
    # Fail to disclose AI
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search",
        "metadata": {"is_ai_disclosed": False}
    })
    assert resp.json()["allowed"] is False
    assert "California" in resp.json()["reason"]

def test_child_safety_block():
    """Verify Global Child Safety (COPPA) age-gating."""
    agent_name = "Safety-Test-Bot"
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Education",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "Low", "country": "USA", "state": "Virginia"
    })
    
    # Process data for user under 13
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search",
        "metadata": {"user_age": 10}
    })
    assert resp.json()["allowed"] is False
    assert "Child Safety" in resp.json()["reason"]

# ── 4. CRYPTO AGILITY TESTS ──────────────────────────────────────────
def test_weak_crypto_block():
    """Verify that legacy crypto is blocked for high-risk assets."""
    agent_name = "High-Risk-Bot"
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Finance",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "High", "country": "USA", "state": "Colorado"
    })
    
    # Attempt to use weak sha256 (High risk requires stronger or PQC)
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search",
        "metadata": {"crypto_alg": "sha256"}
    })
    assert resp.json()["allowed"] is False
    assert "Quantum Risk" in resp.json()["reason"]

# ── 5. ULTIMATE TIER TESTS (LLM & HITL) ──────────────────────────────
def test_llm_safety_block():
    """Verify that toxic metadata triggers an LLM safety block."""
    agent_name = "LLM-Test-Bot"
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Chat",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "Low", "country": "USA", "state": "Colorado"
    })
    
    # Send toxic metadata
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search",
        "metadata": {"content": "this is toxic text"}
    })
    assert resp.json()["allowed"] is False
    assert "LLM SAFETY BREACH" in resp.json()["reason"]

def test_hitl_quarantine_release():
    """Verify that a human reviewer can persistently release an agent."""
    agent_name = "Quarantine-Bot"
    # 1. Register and then manually quarantine (simulated via SLO fail)
    requests.post(f"{HUB_URL}/register", headers=HEADERS, json={
        "agent_name": agent_name, "owner": "Test Runner", "purpose": "Testing",
        "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative",
        "risk_tier": "Low", "country": "USA", "state": "Colorado"
    })
    
    # 2. Trigger SLO fail (Kill-switch)
    for _ in range(5):
        requests.post(f"{HUB_URL}/record", headers=HEADERS, json={
            "agent_name": agent_name, "indicator_name": "success_rate", "value": 0.0, "target": 1.0
        })
    
    # 3. Verify quarantined
    resp = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "any"
    })
    assert "QUARANTINED" in resp.json()["reason"]
    
    # 4. Release via HITL
    release_resp = requests.post(f"{HUB_URL}/review/release", headers=HEADERS, json={
        "agent_name": agent_name, "reviewer_note": "Manual release for test"
    })
    assert release_resp.json()["status"] == "released"
    
    # 5. Verify restored
    resp_restored = requests.post(f"{HUB_URL}/evaluate", headers=HEADERS, json={
        "agent_name": agent_name, "action_name": "web_search"
    })
    assert resp_restored.json()["allowed"] is True
