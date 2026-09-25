import logging
import jwt
from typing import Optional
from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

security = HTTPBearer(auto_error=False)

def verify_supabase_jwt(token: str) -> dict:
    """
    Verifies a Supabase JWT token using the symmetric secret.
    Raises HTTPException 401 if invalid.
    """
    secret = settings.supabase_jwt_secret
    if not secret:
        logger.error("SUPABASE_JWT_SECRET is not configured.")
        raise HTTPException(status_code=500, detail="Auth configuration error")

    try:
        # Supabase uses HS256 for symmetric secrets.
        # We enforce algorithms=["HS256"] and supply the secret string.
        # Ensure audience is correctly checked if needed. For now, audience 'authenticated' is standard in supabase
        decoded = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_signature": True, "verify_aud": False}
        )
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid JWT: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.exception(f"Error decoding JWT: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> dict:
    """
    FastAPI dependency to require a valid Supabase JWT token.
    Returns the decoded token payload (containing sub/user_id).
    """
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
        
    token = credentials.credentials
    user_payload = verify_supabase_jwt(token)
    return user_payload

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from sqlalchemy import select
from models.policyholder import Policyholder
import uuid

async def get_current_policyholder(
    payload: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Policyholder:
    auth_user_id_str = payload.get("sub")
    if not auth_user_id_str:
        raise HTTPException(status_code=401, detail="Invalid token payload (missing sub)")
    try:
        auth_user_id = uuid.UUID(auth_user_id_str)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid sub format")
    
    # 1. Look up existing policyholder
    ph = await db.scalar(select(Policyholder).where(Policyholder.auth_user_id == auth_user_id))
    
    # 2. Create if not exists (Idempotent profile creation)
    if not ph:
        ph = Policyholder(
            auth_user_id=auth_user_id,
            display_name=payload.get("email") or "New Policyholder",
            phone_verified=False
        )
        db.add(ph)
        await db.flush()
        
        # Hackathon: Automatically provision a Demo Policy and Wallet
        from models.policy import Policy, PolicyStatus, TriggerRule
        from models.wallet import Wallet
        import uuid
        from datetime import datetime, timezone
        
        policy = Policy(
            policyholder_id=ph.id,
            region_id=uuid.UUID("00000000-0000-0000-0000-000000000001"), # Demo region
            name="Kaveri Delta Flood Parametric Insurance 2026",
            status=PolicyStatus.ACTIVE,
            payout_amount_paise=1_000_000,
            currency="INR",
            valid_from=datetime(2026, 1, 1, tzinfo=timezone.utc),
            valid_until=datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc),
        )
        db.add(policy)
        await db.flush()
        
        rule = TriggerRule(
            policy_id=policy.id,
            metric="rainfall",
            threshold_value=100.0,
            threshold_operator=">=",
            unit="mm",
            observation_window_minutes=60,
            consensus_quorum=2,
            consensus_tolerance=5.0,
        )
        db.add(rule)
        await db.flush()
        
        wallet = Wallet(
            policy_id=policy.id,
            currency="INR",
            balance_paise=0,
        )
        db.add(wallet)
        await db.flush()
        
    return ph
