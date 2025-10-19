"""
Simplified security utilities – bcrypt temporarily disabled.
Uses SHA-256 for hashing; easy to switch back later.
"""

import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config import settings
from app.database import get_database
from Crypto.Cipher import AES
import base64

logger = logging.getLogger(__name__)
security = HTTPBearer(auto_error=False)

# ============================================================
# 🔹 PASSWORD HANDLING  (temporary SHA-256)
# ============================================================

def get_password_hash(password: str) -> str:
    """Return SHA-256 hash of password."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare SHA-256 hashes."""
    if not hashed_password:
        return False
    return get_password_hash(plain_password) == hashed_password


# ============================================================
# 🔹 JWT CREATION / DECODING
# ============================================================

def _build_jwt_secret() -> str:
    return (settings.JWT_SECRET_KEY + settings.AES_ENCRYPTION_KEY)[:64]

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})
    return jwt.encode(to_encode, _build_jwt_secret(), algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7))
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
    return jwt.encode(to_encode, _build_jwt_secret(), algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> dict:
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
# 🔹 TOKEN / USER HELPERS
# ============================================================

async def get_current_user_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, str]]:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return {"email": email, "role": payload.get("role"), "user_id": payload.get("user_id")}

async def get_current_user(token_data: Dict[str, str] = Depends(get_current_user_token),
                           db: AsyncIOMotorDatabase = Depends(get_database)) -> dict:
    if not token_data:
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    user = await db.users.find_one({"email": token_data["email"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User inactive")
    return user

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    return current_user

async def get_current_user_or_none(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
                                   db: AsyncIOMotorDatabase = Depends(get_database)) -> Optional[dict]:
    if not credentials:
        return None
    try:
        token_data = decode_token(credentials.credentials)
        return await db.users.find_one({"email": token_data.get("sub")})
    except Exception:
        return None


# ============================================================
# 🔹 ROLE-BASED ACCESS
# ============================================================

def require_role(allowed_roles: List[str]):
    async def checker(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role")
        if role not in allowed_roles:
            raise HTTPException(status_code=403, detail=f"Allowed roles: {', '.join(allowed_roles)}")
        return current_user
    return checker

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


# ============================================================
# 🔹 AES ENCRYPTION HELPERS
# ============================================================

def _pad(data: bytes) -> bytes:
    return data + b"\0" * (16 - len(data) % 16)

def encrypt_sensitive_data(plain_text: str) -> str:
    if not plain_text:
        return plain_text
    key = settings.AES_ENCRYPTION_KEY[:32].encode()
    iv = key[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(_pad(plain_text.encode()))
    return base64.b64encode(encrypted).decode()

def decrypt_sensitive_data(encrypted_text: str) -> str:
    if not encrypted_text:
        return encrypted_text
    key = settings.AES_ENCRYPTION_KEY[:32].encode()
    iv = key[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_text))
    return decrypted.rstrip(b"\0").decode()
