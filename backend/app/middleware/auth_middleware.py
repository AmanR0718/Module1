"""
backend/app/middleware/auth_middleware.py
JWT Authentication Middleware and Current User Dependency
"""

from fastapi import Request, HTTPException, status, Depends
from typing import Optional, Dict
from app.core.database import get_database
from app.utils.security import decode_token
import logging

logger = logging.getLogger(__name__)


async def get_current_user_from_request(request: Request) -> Optional[Dict]:
    """
    Extract and validate the authenticated user from the incoming request.

    This function:
    - Reads the Authorization header.
    - Validates Bearer scheme and JWT format.
    - Decodes the token to extract email/user ID.
    - Fetches user data from MongoDB.
    - Returns the user dict if valid, or raises HTTPException otherwise.
    """

    authorization: str = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Split into scheme and token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Decode JWT token
        token_data = decode_token(token)

        # Check expiration handled in decode_token()
        if not token_data or not token_data.get("email"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        db = get_database()
        user = await db.users.find_one({"email": token_data["email"]})

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Optional: mask sensitive fields
        user.pop("password", None)
        user["_id"] = str(user["_id"])  # Convert ObjectId to string if needed

        return user

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Malformed Authorization header",
        )

    except HTTPException:
        # Re-raise explicit FastAPI exceptions
        raise

    except Exception as e:
        logger.error(f"Authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ------------------------------------------------------
# Dependency for route protection
# ------------------------------------------------------
async def get_current_active_user(user: dict = Depends(get_current_user_from_request)):
    """
    Dependency to ensure the current user is active.
    Example use:
        @router.get("/me", dependencies=[Depends(get_current_active_user)])
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing credentials",
        )

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user
