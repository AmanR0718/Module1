"""
backend/app/utils/security.py
Handles password hashing, JWT creation/verification, and role-based authorization.
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config import settings
from app.database import get_database
import logging

# ============================================================
# 🔹 CONFIGURATION
# ============================================================

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)  # Graceful failure for optional auth


# ============================================================
# 🔹 PASSWORD HANDLING
# ============================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


# ============================================================
# 🔹 JWT CREATION
# ============================================================

def _build_jwt_secret() -> str:
    """Combine JWT and AES secrets for stronger signing key."""
    return (settings.JWT_SECRET_KEY + settings.AES_ENCRYPTION_KEY)[:64]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    })
    return jwt.encode(to_encode, _build_jwt_secret(), algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a long-lived JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    })
    return jwt.encode(to_encode, _build_jwt_secret(), algorithm=settings.JWT_ALGORITHM)


# ============================================================
# 🔹 JWT DECODING
# ============================================================

def decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    try:
        return jwt.decode(token, _build_jwt_secret(), algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        logger.warning(f"Invalid JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ============================================================
# 🔹 TOKEN DEPENDENCIES
# ============================================================

def get_current_user_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[Dict[str, str]]:
    """Extract and validate user token from Authorization header."""
    if not credentials:
        return None

    token = credentials.credentials
    payload = decode_token(token)

    email = payload.get("sub")
    role = payload.get("role")
    user_id = payload.get("user_id")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    return {"email": email, "role": role, "user_id": user_id}


async def get_current_user(
    token_data: Dict[str, str] = Depends(get_current_user_token),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> dict:
    """Retrieve the current authenticated user from the database."""
    if not token_data:
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    user = await db.users.find_one({"email": token_data["email"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is inactive")

    return user


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Return the current active user."""
    return current_user


async def get_current_user_or_none(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> Optional[dict]:
    """
    Optional dependency for routes that can be accessed without authentication.
    Returns `None` if user is not authenticated.
    """
    if not credentials:
        return None
    try:
        token_data = decode_token(credentials.credentials)
        user = await db.users.find_one({"email": token_data.get("sub")})
        return user
    except Exception:
        return None


# ============================================================
# 🔹 ROLE-BASED ACCESS CONTROL
# ============================================================

def require_role(allowed_roles: List[str]):
    """Dependency factory to check if user has one of the required roles."""
    async def role_checker(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role")
        if role not in allowed_roles:
            logger.warning(f"Access denied for role: {role} (Required: {allowed_roles})")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Allowed roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


# Common role-specific helpers
async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


async def require_farmer(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "farmer":
        raise HTTPException(status_code=403, detail="Farmer access required")
    return current_user


async def require_chief(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user.get("role") != "chief":
        raise HTTPException(status_code=403, detail="Chief access required")
    return current_user
