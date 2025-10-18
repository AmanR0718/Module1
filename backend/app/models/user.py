"""
backend/app/models/user.py
Pydantic models for user management, authentication, and authorization.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum
from bson import ObjectId

# Import the fixed PyObjectId from common module
from app.models.common import PyObjectId


# ============================================================
# ENUMS
# ============================================================
class UserRole(str, Enum):
    """User roles in the system"""
    ADMIN = "admin"
    FARMER = "farmer"
    CHIEF = "chief"
    OPERATOR = "operator"


# ============================================================
# BASE MODELS
# ============================================================
class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr = Field(..., description="User's email address")
    full_name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")
    role: UserRole = Field(..., description="User role within the system")
    phone_number: Optional[str] = Field(None, description="User's phone number")


class UserCreate(UserBase):
    """Model for creating new users"""
    password: str = Field(..., min_length=6, max_length=100, description="User password (plain text for input)")

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str):
        """Ensure password meets strength requirements"""
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v


class UserUpdate(BaseModel):
    """Model for updating existing users"""
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    full_name: Optional[str] = Field(None, description="Updated full name")
    phone_number: Optional[str] = Field(None, description="Updated phone number")
    password: Optional[str] = Field(None, min_length=6, max_length=100, description="New password")
    is_active: Optional[bool] = Field(None, description="User activation status")


# ============================================================
# USER RESPONSE MODELS
# ============================================================
class User(UserBase):
    """User response model for API responses"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    is_active: bool = Field(default=True, description="Whether the user account is active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "email": "admin@example.com",
                "full_name": "John Banda",
                "role": "admin",
                "phone_number": "+260971234567",
                "is_active": True,
                "created_at": "2025-10-14T12:00:00Z",
                "updated_at": "2025-10-14T12:00:00Z",
            }
        }
    )


class UserInDB(User):
    """Internal user model (with hashed password)"""
    hashed_password: str = Field(..., description="Hashed password for authentication")

    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
    )


# ============================================================
# AUTHENTICATION & TOKEN MODELS
# ============================================================
class Token(BaseModel):
    """JWT token response model"""
    access_token: str = Field(..., description="JWT access token string")
    refresh_token: Optional[str] = Field(None, description="Optional JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type (usually 'bearer')")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


class TokenData(BaseModel):
    """JWT payload data model"""
    email: Optional[str] = Field(None, description="User's email embedded in token")
    role: Optional[UserRole] = Field(None, description="User's role embedded in token")
    user_id: Optional[str] = Field(None, description="User ID for internal references")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "role": "farmer",
                "user_id": "507f1f77bcf86cd799439011"
            }
        }
    )


# ============================================================
# LOGIN REQUEST MODEL
# ============================================================
class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@example.com",
                "password": "SecurePass123"
            }
        }
    )


# ============================================================
# USER RESPONSE WITH STATS
# ============================================================
class UserWithStats(User):
    """User model with additional statistics"""
    total_farmers_registered: Optional[int] = Field(0, description="Total farmers registered by this operator")
    last_activity: Optional[datetime] = Field(None, description="Last activity timestamp")
    
    model_config = ConfigDict(
        populate_by_name=True,
        from_attributes=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
    )