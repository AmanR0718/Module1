"""
backend/app/routes/auth.py
Authentication & Authorization routes for the Zambian Farmer Support System.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import logging

from app.models.user import (
    UserCreate,
    User,
    UserInDB,
    Token,
    UserRole,
)
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.database import get_database

# ---------------------------------------------------------
# Router setup
# ---------------------------------------------------------
router = APIRouter(prefix="/api/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# Helper dependencies
# ---------------------------------------------------------
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> UserInDB:
    """Return the current authenticated user from JWT token."""
    try:
        token_data = decode_token(token)
        email = token_data.get("email") or token_data.get("sub")

        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing user identity in token.",
            )

        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or account removed.",
            )

        return UserInDB(**user)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth token validation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
        )


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
) -> UserInDB:
    """Ensure user account is active."""
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="User account is deactivated.")
    return current_user


def require_role(allowed_roles: List[str]):
    """Factory for role-based access control dependency."""

    async def role_checker(current_user: UserInDB = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_roles}",
            )
        return current_user

    return role_checker


# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Register a new user.
    - In production, restricted to Admin role.
    """
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered.")

    hashed_password = get_password_hash(user.password)

    user_doc = {
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "phone_number": user.phone_number,
        "hashed_password": hashed_password,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    return User(**user_doc)


# ---------------------------------------------------------
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database),
):
    """
    Authenticate a user and return JWT tokens.
    """
    user = await db.users.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    payload = {
        "sub": user["email"],
        "role": user["role"],
        "user_id": str(user["_id"]),
    }

    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


# ---------------------------------------------------------
@router.get("/me", response_model=User, status_code=status.HTTP_200_OK)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """
    Return details of the currently logged-in user.
    """
    return current_user


# ---------------------------------------------------------
@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
async def refresh_token_endpoint(refresh_token: str, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Refresh an access token using a valid refresh token.
    """
    try:
        token_data = decode_token(refresh_token)

        # Validate token type
        if token_data.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token type. Must be a refresh token.",
            )

        email = token_data.get("email") or token_data.get("sub")
        role = token_data.get("role")

        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found.",
            )

        payload = {
            "sub": email,
            "role": role,
            "user_id": str(user["_id"]),
        }

        new_access_token = create_access_token(payload)
        new_refresh_token = create_refresh_token(payload)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token.",
        )
