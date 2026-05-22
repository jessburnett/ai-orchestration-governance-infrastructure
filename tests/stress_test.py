import requests
import concurrent.futures
import time
import random

HUB_URL = "http://localhost:8000"
AGENT_NAME = "Stress-Test-Agent"

def register_test_agent():
    requests.post(f"{HUB_URL}/register", json={
        "agent_name": AGENT_NAME,
        "owner": "Stress Engine",
        "purpose": "Load testing",
        "scope": "global",
        "caf_phase": "Manage",
        "ai_type": "Predictive",
        "risk_tier": "Low",
        "country": "USA",
        "state": "Colorado"
    })

def send_request(i):
    # Randomize payload to stress OPA logic
    is_malicious = random.random() < 0.3
    metadata = {"query": "Safe search"}
    if is_malicious:
        metadata = {"query": "Malicious SSN leak 000-00-0000"}
    
    # Add Crypto metadata for agility check
    metadata["crypto_alg"] = "sha256"
    metadata["is_ai_disclosed"] = True

    start = time.time()
    try:
        resp = requests.post(f"{HUB_URL}/evaluate", json={
            "agent_name": AGENT_NAME,
            "action_name": "web_search",
            "metadata": metadata
        }, timeout=1)
        latency = (time.time() - start) * 1000
        return resp.status_code, latency
    except Exception as e:
        return 500, 0

def run_stress_test(total_requests=500, workers=10):
    print(f"🔥 Starting Stress Test: {total_requests} requests, {workers} concurrent workers...")
    register_test_agent()
    
    start_time = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(send_request, i) for i in range(total_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    total_time = time.time() - start_time
    latencies = [r[1] for r in results if r[0] == 200]
    
    print("\n📊 Stress Test Results:")
    print(f"   - Total Time: {total_time:.2f}s")
    print(f"   - Throughput: {len(results)/total_time:.1f} req/s")
    print(f"   - Success Rate: {(len(latencies)/len(results))*100:.1f}%")
    if latencies:
        print(f"   - Avg Latency: {sum(latencies)/len(latencies):.1f}ms")
        print(f"   - P95 Latency: {sorted(latencies)[int(len(latencies)*0.95)]:.1f}ms")
    print("\n✅ Stress Test Complete. Check the Dashboard for real-time telemetry flood.")

if __name__ == "__main__":
    run_stress_test()
