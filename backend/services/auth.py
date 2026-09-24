import logging
import jwt
from typing import Optional
from fastapi import Request, HTTPException, Security
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
