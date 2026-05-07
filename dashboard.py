import streamlit as st
import requests
import pandas as pd
import time
import os
import plotly.express as px
import plotly.graph_objects as go
import sqlite3

st.set_page_config(page_title="AI Orchestration Governance Infrastructure (AOGI)", layout="wide")

# Use localhost for internal container communication
HUB_URL = os.getenv("HUB_URL", "http://localhost:8000")
API_KEY = os.getenv("HUB_API_KEY", "agt-secret-key-2024")

# ── Functions ─────────────────────────────────────────────────────────

def fetch_data(retries=1):
    headers = {"X-API-KEY": API_KEY}
    try:
        resp = requests.get(f"{HUB_URL}/measurements", headers=headers, timeout=3)
        if resp.status_code == 200:
            return resp.json()
        else:
            st.session_state['last_error'] = f"Handshake Failed: HTTP {resp.status_code}"
    except Exception as e:
        st.session_state['last_error'] = f"Handshake Failed: {e}"
    return []

def safe_filter(df, cols):
    """Safely filters a DataFrame for existing columns to prevent KeyErrors."""
    existing = [c for c in cols if c in df.columns]
    return df[existing]

# ── Sidebar Command Center ────────────────────────────────────────────

with st.sidebar:
    st.header("🏛️ AOGI Command Center")
    mode = st.radio("Strategic Pillars", [
        "1. AI Strategy (Executive View)", 
        "2. AI Plan (Ethics Onboarding)", 
        "3. Govern AI (Safety Control)", 
        "4. Secure AI (Jurisdiction Audit)",
        "5. Manage AI (Safety SLOs)"
    ])
    refresh_rate = st.slider("Cycle Rate (sec)", 0, 10, 2)
    
    st.markdown("---")
    
    # --- 📊 Pillar 6: Strategic Data Analytics (Moved to Sidebar) ---
    with st.expander("📊 Strategic Data Analytics"):
        data = fetch_data()
        if not data:
            st.info("No strategic data available.")
        else:
            df = pd.DataFrame(data)
            if 'country' in df.columns and 'agent_name' in df.columns:
                geo_df = df[['agent_name', 'country']].drop_duplicates()
                geo_counts = geo_df.groupby('country').count().reset_index()
                fig_map = px.choropleth(geo_counts, locations="country", locationmode="country names", 
                                        color="agent_name", hover_name="country", 
                                        color_continuous_scale=px.colors.sequential.Viridis)
                fig_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=200)
                st.plotly_chart(fig_map, use_container_width=True)
            else:
                st.info("Awaiting jurisdictional data.")

    # --- 🏛️ Pillar 7: HITL Review Portal (Moved to Sidebar) ---
    with st.expander("🏛️ HITL Review Portal"):
        conn = sqlite3.connect("governance.db")
        conn.row_factory = sqlite3.Row
        quarantined = conn.execute("SELECT * FROM agents WHERE status = 'quarantined'").fetchall()
        conn.close()
        
        if not quarantined:
            st.success("✅ Quarantine Clear.")
        else:
            for agent in quarantined:
                st.warning(f"🚨 {agent['name']}")
                note = st.text_input("Reviewer Note", key=f"side_note_{agent['name']}")
                if st.button("Release", key=f"side_btn_{agent['name']}"):
                    headers = {"X-API-KEY": API_KEY}
                    requests.post(f"{HUB_URL}/review/release", headers=headers, json={
                        "agent_name": agent['name'], "reviewer_note": note
                    }, timeout=5)
                    st.rerun()

    # --- 🛠️ Debug Console ---
    with st.expander("🛠️ System Debug Console"):
        if st.button("Clear Global Logs"):
            try:
                resp = requests.post(f"{HUB_URL}/clear", headers={"X-API-KEY": API_KEY}, timeout=3)
                if resp.status_code == 200:
                    st.success("Cleared!")
                    st.rerun()
            except: st.error("Failed.")
            
        st.write(f"Hub: {HUB_URL}")
        if st.button("Handshake Test"):
            try:
                r = requests.get(f"{HUB_URL}/health", headers={"X-API-KEY": API_KEY}, timeout=3)
                st.write(f"Srv: {r.json().get('service')}")
            except Exception as e: st.error(f"Fail: {e}")

# ── Main UI ───────────────────────────────────────────────────────────

if mode == "1. AI Strategy (Executive View)":
    st.title("🏗️ AI Orchestration Governance Infrastructure")
    st.markdown("### Executive Fleet Integrity & Governance Audit")
    st.markdown("---")
    
    data = fetch_data()
    if not data:
        st.info("Waiting for strategic data... (Run a Verification below)")
    else:
        df = pd.DataFrame(data)
        st.success("🏆 **Fleet Governance Certification: ETHICALLY ACTIVE**")
        
        c1, c2, c3, c4 = st.columns(4)
        total_agents = df['agent_name'].nunique() if 'agent_name' in df.columns else 0
        success_df = df[df['indicator_name'] == 'success_rate'] if 'indicator_name' in df.columns else pd.DataFrame()
        avg_sr = (success_df['value'].mean() * 100) if not success_df.empty else 0
        threats = len(df[df['indicator_name'] == 'security_threat']) if 'indicator_name' in df.columns else 0
        
        c1.metric("Ethical Assets", total_agents)
        c2.metric("Fleet Integrity", f"{avg_sr:.1f}%")
        c3.metric("Safety Violations", threats)
        c4.metric("Safety Status", "SECURE" if threats == 0 else "AUDIT REQ")

    st.markdown("---")
    if st.button("🚀 Run Global Ethics & Safety Verification"):
        with st.status("Performing Cross-Jurisdictional Ethics Audit...", expanded=True) as status:
            headers = {"X-API-KEY": API_KEY}
            st.write("📋 **AI Plan**: Registering 'California-Chatbot'...")
            try:
                requests.post(f"{HUB_URL}/register", headers=headers, json={
                    "agent_name": "CA-Chatbot-Test", "owner": "Privacy Office", "purpose": "Customer Support",
                    "scope": "restricted", "caf_phase": "Adopt", "ai_type": "Generative", "risk_tier": "Medium",
                    "country": "USA", "state": "California"
                }, timeout=5)
            except: pass
            
            st.write("⚖️ **Govern AI**: Testing California Disclosure Rule...")
            try:
                requests.post(f"{HUB_URL}/evaluate", headers=headers, json={
                    "agent_name": "CA-Chatbot-Test", "action_name": "web_search",
                    "metadata": {"is_ai_disclosed": False} 
                }, timeout=5)
            except: pass
            
            st.write("👶 **Secure AI**: Testing Global Child Safety (COPPA)...")
            try:
                requests.post(f"{HUB_URL}/evaluate", headers=headers, json={
                    "agent_name": "CA-Chatbot-Test", "action_name": "web_search",
                    "metadata": {"user_age": 10} 
                }, timeout=5)
            except: pass

            status.update(label="✅ Audit Complete!", state="complete", expanded=False)
        time.sleep(1)
        st.rerun()

elif mode == "2. AI Plan (Ethics Onboarding)":
    st.title("🏗️ AI Plan: Ethics & Compliance")
    with st.form("onboarding_form"):
        agent_name = st.text_input("Asset Name")
        owner = st.text_input("Ethical Owner")
        col1, col2 = st.columns(2)
        country = col1.selectbox("Country", ["USA", "EU", "UK", "Other"])
        state = col2.text_input("State", value="California")
        purpose = st.text_area("Strategic Purpose")
        submitted = st.form_submit_button("Submit Approval")
        if submitted:
            headers = {"X-API-KEY": API_KEY}
            try:
                requests.post(f"{HUB_URL}/register", headers=headers, json={
                    "agent_name": agent_name, "owner": owner, "purpose": purpose,
                    "scope": "restricted", "caf_phase": "Ready", "ai_type": "Generative", "risk_tier": "Medium",
                    "country": country, "state": state
                }, timeout=5)
                st.success("✅ Registered.")
            except: st.error("Fail.")

elif mode == "3. Govern AI (Safety Control)":
    st.title("🛡️ Govern AI: Safety Control Plane")
    data = fetch_data()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(safe_filter(df, ['agent_name', 'owner', 'country', 'state', 'purpose']).drop_duplicates(), use_container_width=True)
    else: st.info("No active data.")

elif mode == "4. Secure AI (Jurisdiction Audit)":
    st.title("⚖️ Secure AI: Compliance Audit")
    data = fetch_data()
    if data:
        df = pd.DataFrame(data)
        threat_df = df[df['indicator_name'] == 'security_threat'] if 'indicator_name' in df.columns else pd.DataFrame()
        if threat_df.empty: st.info("System is STABLE.")
        else: st.dataframe(safe_filter(threat_df, ['timestamp', 'agent_name', 'metadata']), use_container_width=True)
    else: st.info("No data.")

elif mode == "5. Manage AI (Safety SLOs)":
    st.title("⚙️ Manage AI: Safety SLOs")
    
    if st.button("🔥 Run Infrastructure Stress Test"):
        with st.status("Simulating Load...", expanded=True) as status:
            headers = {"X-API-KEY": API_KEY}
            total_req = 10
            for i in range(total_req):
                metadata = {"user_age": 25 if i % 3 != 0 else 10, "is_ai_disclosed": True}
                try:
                    requests.post(f"{HUB_URL}/evaluate", headers=headers, json={
                        "agent_name": "Stress-Bot", "action_name": "web_search", "metadata": metadata
                    }, timeout=2)
                except: pass
            status.update(label="✅ Stress Test Complete!", state="complete", expanded=False)
        st.rerun()

    data = fetch_data()
    if data:
        df = pd.DataFrame(data)
        if 'agent_name' in df.columns:
            for agent in df['agent_name'].unique():
                agent_df = df[df['agent_name'] == agent]
                with st.expander(f"Report: {agent}"):
                    sr_df = agent_df[agent_df['indicator_name'] == 'success_rate'] if 'indicator_name' in agent_df.columns else pd.DataFrame()
                    if not sr_df.empty: st.metric("Ethical Integrity", f"{(sr_df['value'].mean() * 100):.1f}%")
    else: st.info("No operational data.")

# ── Strategic Auto-Refresh ───────────────────────────────────────────
if refresh_rate > 0:
    time.sleep(refresh_rate)
    st.rerun()
