from pydantic import BaseModel
from typing import Optional, List

class Chief(BaseModel):
    chief_name: str
    tribal_affiliation: str
    province: str
    district: str
    chiefdom: str
    phone: Optional[str] = None
    email: Optional[str] = None
    jurisdiction_boundaries: Optional[dict] = None
    palace_location: Optional[dict] = None  # GPS coordinates
    
    class Config:
        populate_by_name = True


# ============================================
# File: backend/app/utils/security.py
# ============================================
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from typing import Optional
from app.config import settings
from app.models.user import TokenData
from fastapi import HTTPException, status
from cryptography.fernet import Fernet
import base64

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

# JWT Token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> TokenData:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        return TokenData(email=email, role=role)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

# AES Encryption for sensitive data (NRC numbers)
def get_cipher():
    """Get Fernet cipher for encryption"""
    key = base64.urlsafe_b64encode(settings.AES_ENCRYPTION_KEY.encode()[:32].ljust(32, b'0'))
    return Fernet(key)

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like NRC numbers"""
    cipher = get_cipher()
    encrypted = cipher.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    cipher = get_cipher()
    decrypted = cipher.decrypt(base64.urlsafe_b64decode(encrypted_data))
    return decrypted.decode()