import json
import httpx
import uuid
import time
import jwt
import hmac
import hashlib
import sys
from datetime import datetime

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

    client = httpx.Client(base_url="https://api.terrafluxapp.xyz", timeout=30.0)
    
    print(f"User A: {user_a}")
    
    # 1. Identity & Wallet Creation
    print("Fetching Identity (creates wallet if missing)...")
    resp = client.get("/me", headers={"Authorization": f"Bearer {token_a}"})
    if resp.status_code != 200:
        print(f"Identity fetch failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    identity = resp.json()
    wallet_id = identity["wallet_id"]
    print(f"Wallet created: {wallet_id}")
    
    # Check pre-settlement balance
    wallet_data = resp.json()
    print(f"Wallet data: {wallet_data}")
    pre_balance = wallet_data.get("balance_paise", wallet_data.get("balance", 0))

    # 2. Create policy
    print("Creating policy...")
    resp = client.post("/policies", json={
        "region_id": "b2000000-0000-0000-0000-000000000001",
        "name": "Prod Settlement Policy",
        "premium_amount_paise": 50000,
        "coverage_amount_paise": 1000000,
        "currency": "INR",
        "start_at": "2026-01-01T00:00:00Z",
        "end_at": "2026-12-31T23:59:59Z",
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    policy = resp.json()
    if "policy_id" not in policy:
        print(resp.text)
    policy_id = policy["policy_id"]
    print(f"Policy created: {policy_id}")
    
    # 2. Create order & verify to activate
    rz_secret = vars.get("RAZORPAY_KEY_SECRET")
    print("Creating Razorpay order to activate policy...")
    resp = client.post(f"/policies/{policy_id}/payments/order", headers={"Authorization": f"Bearer {token_a}"})
    order = resp.json()
    rz_order_id = order["razorpay_order_id"]
    
    import hmac
    import hashlib
    fake_payment_id = f"pay_test_{uuid.uuid4().hex[:8]}"
    msg = f"{rz_order_id}|{fake_payment_id}"
    valid_sig = hmac.new(rz_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    
    resp = client.post(
        f"/policies/{policy_id}/payments/verify",
        json={
            "razorpay_order_id": rz_order_id,
            "razorpay_payment_id": fake_payment_id,
            "razorpay_signature": valid_sig,
        },
        headers={"Authorization": f"Bearer {token_a}"},
    )
    v = resp.json()
    assert v["policy_status"] == "ACTIVE", "Policy failed to activate"
    print("Policy activated!")
    
    # 3. Simulate Weather Event
    print("Running simulation (Payout Trigger)...")
    
    # Use DEMO_SOURCE_IDS
    demo_sources = [
        "c3000000-0000-0000-0000-000000000001",
        "c3000000-0000-0000-0000-000000000002",
        "c3000000-0000-0000-0000-000000000003"
    ]
    
    resp = client.post("/simulations", json={
        "scenario": "NORMAL",
        "policy_id": policy_id,
        "region_id": "b2000000-0000-0000-0000-000000000001",
        "observations": [
            {"source_id": demo_sources[0], "value": 110.0},
            {"source_id": demo_sources[1], "value": 108.0},
            {"source_id": demo_sources[2], "value": 111.0}
        ],
        "observed_at": datetime.utcnow().isoformat() + "Z"
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    if resp.status_code != 200:
        print(f"Simulation failed: {resp.status_code} {resp.text}")
        sys.exit(1)
        
    sim = resp.json()
    # Use json.dumps to avoid unicode printing issues with the rupee symbol on Windows
    print(f"Simulation result: {json.dumps(sim, ensure_ascii=True)}")
    assert sim["trigger"]["status"] == "TRIGGERED", "Policy was not triggered!"
    assert sim["settlement"]["status"] == "SUCCESS", "Settlement was not successful!"
    
    # 4. Check post-settlement balance
    resp = client.get("/wallets/me", headers={"Authorization": f"Bearer {token_a}"})
    post_wallet_data = resp.json()
    post_balance = post_wallet_data.get("balance_paise", post_wallet_data.get("balance", 0))
    print(f"Post-settlement balance: {post_balance}")
    
    assert post_balance == pre_balance + 1000000, "Wallet balance did not increase by exactly 1,000,000 paise!"
    
    # 5. Idempotency Check
    print("Testing idempotency by re-running simulation...")
    resp = client.post("/simulations", json={
        "scenario": "NORMAL",
        "policy_id": policy_id,
        "region_id": "b2000000-0000-0000-0000-000000000001",
        "observations": [
            {"source_id": demo_sources[0], "value": 110.0},
            {"source_id": demo_sources[1], "value": 108.0},
            {"source_id": demo_sources[2], "value": 111.0}
        ],
        "observed_at": datetime.utcnow().isoformat() + "Z"
    }, headers={"Authorization": f"Bearer {token_a}"})
    
    sim2 = resp.json()
    # If the policy already triggered, it might just return the existing trigger or evaluate to same.
    # The crucial part is that the wallet balance should remain exactly the same.
    resp = client.get("/wallets/me", headers={"Authorization": f"Bearer {token_a}"})
    idempotent_wallet_data = resp.json()
    idempotent_balance = idempotent_wallet_data.get("balance_paise", idempotent_wallet_data.get("balance", 0))
    print(f"Idempotent balance: {idempotent_balance}")
    
    assert idempotent_balance == post_balance, "Idempotency failed! Balance changed."
    
    # 6. Test Notifications (Phase 4)
    print("Testing Notifications (Phase 4)...")
    resp = client.get("/notifications", headers={"Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 200, "Failed to get notifications"
    notifs = resp.json()
    print(f"Total Notifications: {notifs['total']}")
    
    # Assert at least one notification exists (since settlement occurred)
    assert notifs['total'] >= 1, "No notifications found after settlement!"
    
    notif = notifs['notifications'][0]
    assert notif['status'] == "UNREAD", "Notification should be UNREAD"
    assert "₹" in notif['message'] or "\u20b9" in notif['message'], "Rupee symbol missing from notification"
    
    # Test acknowledgement
    notif_id = notif['notification_id']
    print(f"Acknowledging notification {notif_id}...")
    ack_resp = client.post(f"/notifications/{notif_id}/acknowledge", headers={"Authorization": f"Bearer {token_a}"})
    assert ack_resp.status_code == 200, "Failed to acknowledge notification"
    ack_data = ack_resp.json()
    assert ack_data['status'] == "ACKNOWLEDGED", "Notification not acknowledged"
    
    # Re-fetch notifications to ensure status updated
    resp = client.get("/notifications", headers={"Authorization": f"Bearer {token_a}"})
    updated_notif = next(n for n in resp.json()['notifications'] if n['notification_id'] == notif_id)
    assert updated_notif['status'] == "ACKNOWLEDGED", "Notification status did not persist"
    
    print("SETTLEMENT PHASE 3F & NOTIFICATION PHASE 4 E2E VERIFICATION COMPLETE!")

if __name__ == "__main__":
    run_prod_e2e()
