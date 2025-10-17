"""
backend/app/routes/password.py
Handles forgot password, reset link, and change password endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from pydantic import EmailStr
from datetime import datetime, timedelta
from jose import jwt
from app.utils.security import get_password_hash, decode_token
from app.database import get_database
from app.config import settings
from app.routes.auth import get_current_active_user

router = APIRouter(prefix="/api/password", tags=["Password Management"])

RESET_TOKEN_EXPIRE_MINUTES = 15  # 15 mins expiry


def create_reset_token(email: str):
    """Generate a short-lived password reset token."""
    expire = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": email, "exp": expire, "type": "password_reset"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/forgot")
async def forgot_password(email: EmailStr, request: Request, db=Depends(get_database)):
    """Send reset link (mocked as console print for now)."""
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token = create_reset_token(email)
    reset_link = f"{request.base_url}api/password/reset?token={token}"
    print(f"🧩 Password reset link (for testing): {reset_link}")

    return {"message": "Password reset link generated", "reset_link": reset_link}


@router.post("/reset")
async def reset_password(token: str = Form(...), new_password: str = Form(...), db=Depends(get_database)):
    """Reset password using token."""
    try:
        payload = decode_token(token)
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")

        email = payload.get("sub")
        hashed_password = get_password_hash(new_password)
        result = await db.users.update_one({"email": email}, {"$set": {"hashed_password": hashed_password}})

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "Password reset successful"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token invalid or expired: {str(e)}")


@router.post("/change")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user=Depends(get_current_active_user),
    db=Depends(get_database),
):
    """Change password for logged-in user."""
    from app.utils.security import verify_password

    user = await db.users.find_one({"email": current_user["email"]})
    if not user or not verify_password(old_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")

    hashed_password = get_password_hash(new_password)
    await db.users.update_one(
        {"email": current_user["email"]},
        {"$set": {"hashed_password": hashed_password, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Password changed successfully"}
