"""Shared config + data helpers for the AOGI Streamlit app.

Single source for hub connection details and the small helpers reused across
every page. Keeps page modules free of duplicated config.
"""
import os

import requests
import streamlit as st

# Use localhost for internal container communication
HUB_URL = os.getenv("HUB_URL", "http://localhost:8000")
API_KEY = os.getenv("HUB_API_KEY", "agt-secret-key-2024")


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
