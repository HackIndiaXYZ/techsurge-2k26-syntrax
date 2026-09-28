"""
Cross-User Security Test for Production
"""
import os
import sys
import uuid
import jwt
import time
import requests
import json

BASE_URL = "https://api.terrafluxapp.xyz"

def get_token(user_id: str) -> str:
    with open('../railway_vars.json', 'r') as f:
        vars = json.load(f)
    jwt_secret = vars.get("SUPABASE_JWT_SECRET")

    token = jwt.encode(
        {"sub": user_id, "role": "authenticated", "iat": int(time.time()), "exp": int(time.time()) + 3600},
        jwt_secret,
        algorithm="HS256",
    )
    return token

def run_cross_user_test():
    user_a = str(uuid.uuid4())
    user_b = str(uuid.uuid4())
    print(f"User A: {user_a}")
    print(f"User B: {user_b}")

    token_a = get_token(user_a)
    token_b = get_token(user_b)

    # 1. User A creates identity and gets wallet
    resp = requests.get(f"{BASE_URL}/me", headers={"Authorization": f"Bearer {token_a}"})
    if resp.status_code != 200:
        print(f"Identity A fetch failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    identity_a = resp.json()
    wallet_id_a = identity_a.get("wallet_id")

    if not wallet_id_a:
        print("User A has no wallet.")
        sys.exit(1)

    print(f"User A wallet: {wallet_id_a}")

    # 2. User B creates identity and gets wallet
    resp = requests.get(f"{BASE_URL}/me", headers={"Authorization": f"Bearer {token_b}"})
    if resp.status_code != 200:
        print(f"Identity B fetch failed: {resp.status_code} {resp.text}")
        sys.exit(1)
    
    identity_b = resp.json()
    wallet_id_b = identity_b.get("wallet_id")

    print(f"User B wallet: {wallet_id_b}")

    # 3. User B tries to access User A's wallet
    print(f"User B trying to access User A wallet {wallet_id_a}...")
    resp = requests.get(f"{BASE_URL}/wallets/{wallet_id_a}", headers={"Authorization": f"Bearer {token_b}"})
    print(f"Response: {resp.status_code}")
    assert resp.status_code in (401, 403, 404), f"Security failure! User B accessed User A wallet: {resp.status_code}"
    print("Cross-user wallet access correctly rejected.")
    
    print("CROSS-USER SECURITY E2E VERIFICATION COMPLETE!")

if __name__ == "__main__":
    run_cross_user_test()
