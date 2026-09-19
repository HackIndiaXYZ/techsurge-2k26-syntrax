import httpx
import json
from datetime import datetime, timezone

def run():
    url = "http://localhost:8000/simulations"
    payload = {
        "scenario": "NORMAL",
        "policy_id": "e5000000-0000-0000-0000-000000000001",
        "region_id": "b2000000-0000-0000-0000-000000000001",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "observations": [
            {"source_id": "c3000000-0000-0000-0000-000000000001", "value": 150.0},
            {"source_id": "c3000000-0000-0000-0000-000000000002", "value": 145.0},
            {"source_id": "c3000000-0000-0000-0000-000000000003", "value": 155.0},
        ]
    }
    
    print(f"POSTing to {url}")
    resp = httpx.post(url, json=payload, timeout=10.0)
    print(f"Status Code: {resp.status_code}")
    print("Response:")
    print(json.dumps(resp.json(), indent=2))

if __name__ == "__main__":
    run()
