from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    OPERATOR = "operator"
    FARMER = "farmer"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool = True
    assigned_provinces: Optional[List[str]] = []
    assigned_districts: Optional[List[str]] = []

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    assigned_provinces: Optional[List[str]] = None
    assigned_districts: Optional[List[str]] = None

class UserInDB(UserBase):
    id: str = Field(alias="_id")
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class User(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None