import time
from typing import Any, Dict, List, Optional
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult

import sys
import os
import requests
sys.path.append(os.path.dirname(__file__))

HUB_URL = os.getenv("HUB_URL")

class GovernanceClient:
    """Client to interact with the Governance Hub (local or remote)."""
    
    def check_action(self, agent_name, action_name, metadata=None):
        if HUB_URL:
            try:
                resp = requests.post(
                    f"{HUB_URL}/evaluate",
                    headers={"X-API-KEY": os.getenv("HUB_API_KEY", "agt-secret-key-2024")},
                    json={
                        "agent_name": agent_name,
                        "action_name": action_name,
                        "metadata": metadata
                    },
                    timeout=2
                )
                data = resp.json()
                return data["allowed"], data["reason"]
            except Exception as e:
                return False, f"Governance Hub unavailable: {e}"
        else:
            # Fallback to local import if no HUB_URL is set
            from ecosystem_hub import hub
    def record_measurement(self, agent_name, indicator_name, value, target, lower_is_better=False):
        if HUB_URL:
            try:
                requests.post(
                    f"{HUB_URL}/record",
                    headers={"X-API-KEY": os.getenv("HUB_API_KEY", "agt-secret-key-2024")},
                    json={
                        "agent_name": agent_name,
                        "indicator_name": indicator_name,
                        "value": value,
                        "target": target,
                        "lower_is_better": lower_is_better
                    },
                    timeout=1
                )
            except:
                pass # Silently fail for recording

gov_client = GovernanceClient()

from agent_sre import SLO, ErrorBudget
from agent_sre.slo.indicators import TaskSuccessRate, ResponseLatency

class AGTCallbackHandler(BaseCallbackHandler):
    """
    LangChain Callback Handler that integrates with the Agent Governance Toolkit.
    
    This handler:
    1. Enforces policies before tool execution.
    2. Records SLO metrics (success rate, latency) automatically.
    """
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        
        # Initialize SLO indicators for this agent
        self.success_rate = TaskSuccessRate(target=0.99, window="1h")
        self.latency = ResponseLatency(target_ms=500, window="1h")
        
        self.slo = SLO(
            name=f"{agent_name}-governance-slo",
            indicators=[self.success_rate, self.latency],
            error_budget=ErrorBudget(total=0.05)
        )
        self._start_times = {}

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Track the start of a chain run."""
        run_id = kwargs.get("run_id")
        self._start_times[run_id] = time.time()
        print(f"⛓️  [LANGCHAIN] Starting chain for {self.agent_name}")

    def on_tool_start(
        self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Check governance policy before a tool runs."""
        tool_name = serialized.get("name")
        print(f"🔍 [LANGCHAIN] Governing tool call: {tool_name}")
        
        allowed, reason = gov_client.check_action(
            self.agent_name, 
            tool_name, 
            {"tool_input": input_str}
        )
        
        if not allowed:
            print(f"🛑 [LANGCHAIN] POLICY VIOLATION: {reason}")
            # In a real LangChain app, you might raise an exception or return a tool error
            raise PermissionError(f"Agent Governance Policy Violation: {reason}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Record success and latency when a chain finishes."""
        run_id = kwargs.get("run_id")
        start_time = self._start_times.pop(run_id, time.time())
        duration_ms = (time.time() - start_time) * 1000
        
        self.latency.record(duration_ms)
        self.success_rate.record_task(success=True)
        
        # Report to central Hub
        gov_client.record_measurement(self.agent_name, "latency", duration_ms, 500, True)
        gov_client.record_measurement(self.agent_name, "success_rate", 1.0, 0.99, False)
        
        print(f"✅ [LANGCHAIN] Chain completed in {duration_ms:.1f}ms")

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Record failure when a chain errors."""
        run_id = kwargs.get("run_id")
        self._start_times.pop(run_id, None)
        
        self.success_rate.record_task(success=False)
        gov_client.record_measurement(self.agent_name, "success_rate", 0.0, 0.99, False)
        print(f"⚠️  [LANGCHAIN] Chain failed: {error}")

# ── Demonstration ──────────────────────────────────────────────────────

if __name__ == "__main__":
    # Initialize our governed handler
    # Rules are centrally managed by the Ecosystem Hub (ecosystem_hub.py)
    handler = AGTCallbackHandler(agent_name="research-assistant")

    print("\n--- LangChain Ecosystem Integration Demo ---")
    
    # Simulate a successful tool call (allowed by default)
    try:
        handler.on_tool_start({"name": "web_search"}, "latest AI news")
        handler.on_chain_start({}, {}, run_id="run1")
        time.sleep(0.1) # Simulate work
        handler.on_chain_end({}, run_id="run1")
    except Exception as e:
        print(f"Caught expected error: {e}")

    # Simulate a blocked tool call
    print("\n--- Testing Blocked Action ---")
    try:
        handler.on_tool_start({"name": "terminal_command"}, "rm -rf /")
    except PermissionError as e:
        print(f"Governance in action: {e}")

    # 3. Check the SLO status
    status = handler.slo.evaluate()
    compliance = handler.success_rate.compliance()
    compliance_str = f"{compliance * 100:.1f}%" if compliance is not None else "N/A"
    
    print(f"\n📊 [SLO STATUS] {status.value}")
    print(f"📈 [COMPLIANCE] {compliance_str}")
