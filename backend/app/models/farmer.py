"""
backend/app/models/farmer.py
Defines all Pydantic models for Farmer data representation and validation.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Dict
from datetime import datetime, date
from enum import Enum
from bson import ObjectId
from pydantic import GetJsonSchemaHandler
from pydantic_core import core_schema


# ============================================================
# ENUMERATIONS
# ============================================================
class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class RegistrationStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    INACTIVE = "inactive"


# ============================================================
# HELPERS
# ============================================================
class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source, _handler):
        return core_schema.no_info_plain_validator_function(cls.validate)

    @classmethod
    def __get_pydantic_json_schema__(cls, _schema, handler: GetJsonSchemaHandler):
        json_schema = handler(_schema)
        json_schema.update(type="string")
        return json_schema

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# ============================================================
# NESTED MODELS
# ============================================================
class PersonalInfo(BaseModel):
    first_name: str = Field(..., description="Farmer's first name")
    middle_name: Optional[str] = Field(None, description="Farmer's middle name")
    last_name: str = Field(..., description="Farmer's last name")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: Gender = Field(..., description="Gender (male, female, other)")
    phone_primary: str = Field(..., description="Primary phone number")
    phone_secondary: Optional[str] = Field(None, description="Secondary phone number")
    email: Optional[EmailStr] = Field(None, description="Email address")


class Address(BaseModel):
    province: str = Field(..., description="Province name")
    district: str = Field(..., description="District name")
    constituency: Optional[str] = Field(None, description="Constituency name")
    ward: Optional[str] = Field(None, description="Ward name")
    village: str = Field(..., description="Village name")
    traditional_authority: Optional[str] = Field(None, description="Traditional authority")
    gps_latitude: Optional[float] = Field(None, description="GPS latitude coordinate")
    gps_longitude: Optional[float] = Field(None, description="GPS longitude coordinate")


class FarmDetails(BaseModel):
    farm_size_hectares: float = Field(..., gt=0, description="Farm size in hectares")
    crops_grown: List[str] = Field(default_factory=list, description="List of crops grown")
    livestock: List[str] = Field(default_factory=list, description="List of livestock")
    has_irrigation: bool = Field(default=False, description="Whether farm has irrigation")
    farming_experience_years: int = Field(..., ge=0, description="Years of farming experience")


# ============================================================
# MAIN FARMER MODELS
# ============================================================
class FarmerBase(BaseModel):
    farmer_id: str = Field(..., description="Unique farmer ID (ZF-XXXX-XXXXXX)")
    nrc_number: str = Field(..., description="National Registration Card number (encrypted if stored)")
    personal_info: PersonalInfo
    address: Address
    farm_details: FarmDetails
    next_of_kin_name: Optional[str] = Field(None, description="Next of kin's full name")
    next_of_kin_phone: Optional[str] = Field(None, description="Next of kin's phone number")
    registration_status: RegistrationStatus = Field(default=RegistrationStatus.PENDING)
    notes: Optional[str] = Field(None, description="Additional registration notes")


class FarmerCreate(FarmerBase):
    """Model used for farmer registration requests"""
    pass


class FarmerUpdate(BaseModel):
    """Partial update model"""
    personal_info: Optional[PersonalInfo] = None
    address: Optional[Address] = None
    farm_details: Optional[FarmDetails] = None
    next_of_kin_name: Optional[str] = None
    next_of_kin_phone: Optional[str] = None
    registration_status: Optional[RegistrationStatus] = None
    notes: Optional[str] = None
    last_modified_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class Farmer(FarmerBase):
    """Database model representation"""
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    qr_code_url: Optional[str] = Field(None, description="Link to farmer QR code image")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User email who created this record")
    last_modified_by: Optional[str] = None

    @field_validator("nrc_number")
    @classmethod
    def sanitize_nrc(cls, v):
        """Ensure NRC number is non-empty before encrypting."""
        if not v or not v.strip():
            raise ValueError("NRC number cannot be empty")
        return v.strip()

    class Config:
        populate_by_name = True
        from_attributes = True
        json_encoders = {ObjectId: str}
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "farmer_id": "ZF-2025-001234",
                "nrc_number": "123456/78/9",
                "personal_info": {
                    "first_name": "John",
                    "middle_name": "T.",
                    "last_name": "Banda",
                    "date_of_birth": "1980-05-15",
                    "gender": "male",
                    "phone_primary": "+260971234567"
                },
                "address": {
                    "province": "Lusaka",
                    "district": "Chilanga",
                    "village": "Ngwerere"
                },
                "farm_details": {
                    "farm_size_hectares": 5.5,
                    "crops_grown": ["maize", "groundnuts"],
                    "livestock": ["cattle", "chickens"],
                    "has_irrigation": False,
                    "farming_experience_years": 15
                },
                "registration_status": "active",
                "created_at": "2025-10-15T08:00:00Z",
                "updated_at": "2025-10-15T08:00:00Z"
            }
        }


# ============================================================
# SEARCH & STATISTICS MODELS
# ============================================================
class FarmerSearchParams(BaseModel):
    """Query parameters for farmer search filters"""
    farmer_id: Optional[str] = None
    nrc_number: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    registration_status: Optional[RegistrationStatus] = None
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, le=500)


class FarmerStats(BaseModel):
    """Statistical summary for dashboard analytics"""
    total_farmers: int
    active_farmers: int
    pending_registrations: int
    farmers_by_province: Dict[str, int]
    farmers_by_district: Dict[str, int]
