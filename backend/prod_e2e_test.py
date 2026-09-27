import json
import httpx
import uuid
import time
import jwt
import hmac
import hashlib
import sys

def run_prod_e2e():
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)

    jwt_secret = vars.get("SUPABASE_JWT_SECRET")
    rz_secret = vars.get("RAZORPAY_KEY_SECRET")

    user_a = str(uuid.uuid4())
    token_a = jwt.encode(
        {"sub": user_a, "role": "authenticated", "iat": int(time.time()), "exp": int(time.time()) + 3600},
        jwt_secret,
        algorithm="HS256",
    )

    client = httpx.Client(base_url="https://api.terrafluxapp.xyz")

    print(f"User A: {user_a}")
    
    # 1. Create policy
    print("Creating policy...")
    resp = client.post("/policies", json={
        "region_id": "b2000000-0000-0000-0000-000000000001",
        "name": "Prod E2E Policy",
        "premium_amount_paise": 50000,
        "coverage_amount_paise": 1000000,
        "currency": "INR",
        "start_at": "2026-10-01T00:00:00Z",
        "end_at": "2026-12-31T23:59:59Z",
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    if resp.status_code != 201:
        print(f"Policy creation failed: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    policy = resp.json()
    policy_id = policy["policy_id"]
    print(f"Policy created: {policy_id} | Status: {policy['status']}")
    
    # 2. Create order
    print("Creating Razorpay order...")
    resp = client.post(f"/policies/{policy_id}/payments/order", headers={"Authorization": f"Bearer {token_a}"})
    if resp.status_code != 201:
        print(f"Order creation failed: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    order = resp.json()
    rz_order_id = order["razorpay_order_id"]
    print(f"Order created: {rz_order_id}")
    
    # 3. Verify payment
    fake_payment_id = f"pay_test_{uuid.uuid4().hex[:8]}"
    msg = f"{rz_order_id}|{fake_payment_id}"
    valid_sig = hmac.new(rz_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    
    print("Verifying payment...")
    resp = client.post(
        f"/policies/{policy_id}/payments/verify",
        json={
            "razorpay_order_id": rz_order_id,
            "razorpay_payment_id": fake_payment_id,
            "razorpay_signature": valid_sig,
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    
    if resp.status_code != 200:
        print(f"Verification failed: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    v = resp.json()
    print(f"Verification success: {v}")
    
    if v["policy_status"] == "ACTIVE":
        print("PROD E2E FLOW SUCCESSFUL!")
    else:
        print("PROD E2E FLOW FAILED: Policy not ACTIVE")
        sys.exit(1)

    print("Checking internal payment record...")
    resp = client.get(
        f"/policies/{policy_id}/payments/status",
        headers={"Authorization": f"Bearer {token_a}"},
    )
    if resp.status_code != 200:
        print(f"Failed to fetch payment status: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    p_status = resp.json()
    print(f"Internal Payment Record: {json.dumps(p_status, indent=2)}")
    
    assert p_status["status"] == "SUCCESS", "Payment record is not SUCCESS"
    assert p_status["provider_order_id"] == rz_order_id, "Order ID mismatch"
    assert p_status["amount_paise"] == 50000, "Amount mismatch"
    print("Phase 3D VERIFICATION COMPLETE!")

if __name__ == "__main__":
    run_prod_e2e()
