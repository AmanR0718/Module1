from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime
from app.models.user import UserCreate, User, Token, UserInDB, UserRole
from app.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.database import get_database

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Get current authenticated user"""
    token_data = decode_token(token)
    db = get_database()
    user = await db.users.find_one({"email": token_data.email})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return UserInDB(**user)

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(allowed_roles: list):
    """Dependency to check user role"""
    async def role_checker(current_user: UserInDB = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    """Register new user (Admin only in production)"""
    db = get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_dict = user.dict(exclude={"password"})
    user_dict.update({
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Insert user
    result = await db.users.insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    
    return User(**user_dict)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    db = get_database()
    
    # Find user
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["email"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=User)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    token_data = decode_token(refresh_token)
    
    # Create new tokens
    access_token = create_access_token(
        data={"sub": token_data.email, "role": token_data.role}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": token_data.email, "role": token_data.role}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
