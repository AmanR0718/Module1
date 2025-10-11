from fastapi import Request, HTTPException, status
from app.utils.security import decode_token
from app.database import get_database
from typing import Optional

async def get_current_user_from_request(request: Request) -> Optional[dict]:
    """Extract and validate user from request"""
    authorization: str = request.headers.get("Authorization")
    
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
        
        token_data = decode_token(token)
        db = get_database()
        user = await db.users.find_one({"email": token_data.email})
        
        return user
    except:
        return None