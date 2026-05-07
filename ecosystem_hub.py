from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import time
import os
import sqlite3
import requests as http_requests
from agent_os.policies import PolicyEvaluator, PolicyDocument, PolicyAction, PolicyDefaults, PolicyRule, PolicyCondition, PolicyOperator

# ── Configuration ─────────────────────────────────────────────────────
OPA_URL = os.getenv("OPA_URL", "http://opa:8181/v1/data/ai_strategy/main")
API_KEY = os.getenv("HUB_API_KEY", "agt-secret-key-2024")
DB_PATH = "governance.db"

app = FastAPI(title="AI Orchestration Governance Infrastructure (AOGI)")

# ── Database Initialization ───────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agents 
                 (name TEXT PRIMARY KEY, owner TEXT, purpose TEXT, scope TEXT, 
                  caf_phase TEXT, ai_type TEXT, risk_tier TEXT, country TEXT, state TEXT, status TEXT)''')
    # Bootstrap default agents if empty
    c.execute("INSERT OR IGNORE INTO agents VALUES (?,?,?,?,?,?,?,?,?,?)", 
              ("Ecosystem-Bootstrap", "System", "Health check", "global", "Manage", "Predictive", "Low", "USA", "Virginia", "active"))
    conn.commit()
    conn.close()

init_db()

# ── Security Middleware ───────────────────────────────────────────────
# @touchpoint security-handshake: Validates X-API-KEY for all strategic endpoints
def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")

# ── Central SRE Storage (In-memory for performance metrics) ───────────
measurements = []

# ── Models ─────────────────────────────────────────────────────────────
class ReviewRequest(BaseModel):
    agent_name: str
    reviewer_note: str

class ActionRequest(BaseModel):
    agent_name: str
    action_name: str
    metadata: Optional[Dict[str, Any]] = None

class ActionResponse(BaseModel):
    allowed: bool
    reason: str
    compliance_score: float

class MeasurementRecord(BaseModel):
    agent_name: str
    indicator_name: str
    value: float
    target: float
    lower_is_better: bool = False
    timestamp: float = None
    metadata: Optional[Dict[str, Any]] = None

class AgentRegistration(BaseModel):
    agent_name: str
    owner: str
    purpose: str
    scope: str
    caf_phase: str
    ai_type: str
    risk_tier: str
    country: str = "USA"
    state: str = "Colorado"

# ── Strategic Content Safety (LLM Mock) ────────────────────────────────
# @touchpoint llm-safety-scan: Performs NLP-based toxicity and bias detection
def scan_content_safety(request: ActionRequest) -> Dict[str, Any]:
    """Simulates an LLM-based safety scan for toxicity, bias, and PII."""
    metadata = request.metadata or {}
    toxicity = 0.0
    bias = 0.0
    
    # Mock heuristics for demonstration
    if "toxic" in str(metadata).lower(): toxicity = 0.9
    if "biased" in str(metadata).lower(): bias = 0.8
    
    return {
        "toxicity_score": toxicity,
        "bias_score": bias,
        "is_flagged": toxicity > 0.7 or bias > 0.7
    }

# ── Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "AOGI Governance Hub", 
        "timestamp": time.time()
    }

@app.post("/evaluate", response_model=ActionResponse)
# @touchpoint governance-decision: The primary evaluation loop for all agent actions
def evaluate_action(request: ActionRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    
    # 1. Identity & Quarantine Check (Persistent Registry)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    reg = conn.execute("SELECT * FROM agents WHERE name = ?", (request.agent_name,)).fetchone()
    conn.close()
    
    if not reg:
        return ActionResponse(allowed=False, reason="Unregistered Agent: No CAF Charter found.", compliance_score=0.0)
    
    reg = dict(reg)
    if reg.get("status") == "quarantined":
        return ActionResponse(allowed=False, reason="AGENT QUARANTINED.", compliance_score=0.0)
    
    # ── Automated SLO Check (Kill Switch) ──────────────────────────────
    agent_history = [m for m in measurements if m["agent_name"] == request.agent_name and m["indicator_name"] == "success_rate"]
    if len(agent_history) >= 5:
        recent_sr = sum(m["value"] for m in agent_history[-5:]) / 5
        if recent_sr < 0.5:
            # Persistent Quarantine with Reason
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE agents SET status = 'quarantined' WHERE name = ?", (request.agent_name,))
            conn.commit()
            conn.close()
            return ActionResponse(allowed=False, reason="🚨 QUARANTINED: Performance below threshold (Kill-Switch triggered).", compliance_score=0.0)

    # ── 1.5 LLM Content Safety Scan ────────────────────────────────────
    safety_audit = scan_content_safety(request)
    if safety_audit["is_flagged"]:
        # Log a safety signal but don't auto-quarantine yet (send to HITL)
        measurements.append({
            "agent_name": request.agent_name, "indicator_name": "safety_violation", "value": 1.0, 
            "target": 0.0, "timestamp": time.time(), "metadata": safety_audit
        })
        return ActionResponse(allowed=False, reason=f"LLM SAFETY BREACH: Toxicity/Bias detected ({safety_audit['toxicity_score']})", compliance_score=0.2)

    # 2. Scoped Access & OPA Legal Audit (CAF + OPA)
    opa_input = {
        "input": {
            "agent_name": request.agent_name,
            "action_name": request.action_name,
            "scope": reg["scope"],
            "risk_tier": reg["risk_tier"],
            "purpose": reg["purpose"],
            "country": reg["country"],
            "state": reg["state"],
            "metadata": request.metadata or {}
        }
    }
    
    # Resilient OPA call with retries
    for attempt in range(3):
        try:
            opa_resp = http_requests.post(OPA_URL, json=opa_input, timeout=2)
            if opa_resp.status_code == 200:
                result = opa_resp.json().get("result", {})
                allowed_by_opa = result.get("allow", False)
                opa_reason = result.get("reason", "OPA: Policy decision enforced.")
                break
        except Exception:
            if attempt == 2:
                return ActionResponse(allowed=False, reason="GOVERNANCE ERROR: OPA unavailable after retries.", compliance_score=0.0)
            time.sleep(1)
    else:
        return ActionResponse(allowed=False, reason="GOVERNANCE ERROR: OPA decision timeout.", compliance_score=0.0)

    if not allowed_by_opa:
        measurements.append({
            "agent_name": request.agent_name, "indicator_name": "security_threat", "value": 1.0, 
            "target": 0.0, "timestamp": time.time(), "metadata": {"reason": opa_reason}
        })
        return ActionResponse(allowed=False, reason=opa_reason, compliance_score=0.1)

    return ActionResponse(allowed=True, reason="Verified Compliant with Global Policy.", compliance_score=1.0)

@app.post("/record")
def record_measurement(record: MeasurementRecord, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    record.timestamp = record.timestamp or time.time()
    measurements.append(record.dict())
    return {"status": "recorded"}

@app.post("/register")
# @touchpoint caf-onboarding: Persistent registration of agent CAF charters
def register_agent(reg: AgentRegistration, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""INSERT OR REPLACE INTO agents 
                     (name, owner, purpose, scope, caf_phase, ai_type, risk_tier, country, state, status)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                     (reg.agent_name, reg.owner, reg.purpose, reg.scope, reg.caf_phase, 
                      reg.ai_type, reg.risk_tier, reg.country, reg.state, "active"))
        conn.commit()
    finally:
        conn.close()
    return {"status": "registered", "agent_name": reg.agent_name}

@app.post("/review/release")
# @touchpoint hitl-review-release: Authorized manual intervention to lift quarantines
def release_quarantine(req: ReviewRequest, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("UPDATE agents SET status = 'active' WHERE name = ?", (req.agent_name,))
        conn.commit()
        # Record the manual intervention
        measurements.append({
            "agent_name": req.agent_name, "indicator_name": "human_intervention", "value": 1.0, 
            "target": 1.0, "timestamp": time.time(), "metadata": {"note": req.reviewer_note}
        })
    finally:
        conn.close()
    return {"status": "released", "agent_name": req.agent_name}

@app.get("/measurements")
def get_measurements():
    # Enrich measurements with persistent CAF data
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    registry = {row["name"]: dict(row) for row in conn.execute("SELECT * FROM agents").fetchall()}
    conn.close()
    
    enriched = []
    for m in measurements:
        reg = registry.get(m["agent_name"], {})
        enriched.append({
            **m, 
            "owner": reg.get("owner", "Unknown"), 
            "caf_phase": reg.get("caf_phase", "Unknown"), 
            "country": reg.get("country", "Unknown"), 
            "state": reg.get("state", "Unknown"),
            "purpose": reg.get("purpose", "No purpose declared.")
        })
    return enriched

@app.post("/clear")
def clear_measurements(x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    global measurements
    measurements = []
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
