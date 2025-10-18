"""
backend/app/models/farmer.py
Defines all Pydantic models for Farmer data representation and validation.
"""

from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
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


class OwnershipType(str, Enum):
    OWNED = "owned"
    LEASED = "leased"
    SHARED = "shared"


class LandType(str, Enum):
    IRRIGATED = "irrigated"
    NON_IRRIGATED = "non-irrigated"

class RegistrationStatus(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    APPROVED = "approved"
    REJECTED = "rejected"


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
    """Personal information"""
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_primary: str = Field(..., pattern=r'^\+260-\d{2}-\d{7}$')
    phone_secondary: Optional[str] = Field(None, pattern=r'^\+260-\d{2}-\d{7}$')
    email: Optional[str] = Field(None, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    date_of_birth: date
    gender: Gender
    nrc_number: str = Field(..., description="National Registration Card number")
    photograph_url: Optional[str] = None

    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v: date) -> date:
        """Ensure farmer is at least 18 years old"""
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('Farmer must be at least 18 years old')
        return v



class Address(BaseModel):
    """Address information"""
    street_village: str = Field(..., description="Street or village name")
    district: str = Field(..., description="District name")
    province: str = Field(..., description="Province name")
    chiefdom: Optional[str] = Field(None, description="Traditional chiefdom")
    postal_code: Optional[str] = Field(None, description="Postal code")
    gps_latitude: Optional[float] = Field(None, description="GPS latitude coordinate")
    gps_longitude: Optional[float] = Field(None, description="GPS longitude coordinate")


class FarmDetails(BaseModel):
    farm_size_hectares: float = Field(..., gt=0, description="Farm size in hectares")
    crops_grown: List[str] = Field(default_factory=list, description="List of crops grown")
    livestock: List[str] = Field(default_factory=list, description="List of livestock")
    has_irrigation: bool = Field(default=False, description="Whether farm has irrigation")
    farming_experience_years: int = Field(..., ge=0, description="Years of farming experience")

class GPSCoordinates(BaseModel):
    """GPS coordinates model"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude")
    altitude: Optional[float] = Field(None, description="Altitude in meters")
    accuracy: Optional[float] = Field(None, description="GPS accuracy in meters")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "latitude": -14.7167,
                "longitude": 28.4333,
                "altitude": 1200.5,
                "accuracy": 5.0
            }
        }
    )

class LandParcel(BaseModel):
    """Individual land parcel information"""
    parcel_id: str = Field(..., description="Unique parcel identifier")
    area: float = Field(..., gt=0, description="Area in hectares")
    land_type: LandType
    ownership_status: OwnershipType
    soil_type: Optional[str] = None
    water_sources: Optional[List[str]] = []
    gps_coordinates: Optional[GPSCoordinates] = None
    lease_period: Optional[str] = Field(None, description="Lease period if leased")
    owner_details: Optional[str] = Field(None, description="Owner details if leased")


class Crop(BaseModel):
    """Crop cultivation details"""
    crop_name: str = Field(..., description="Name of the crop")
    variety: Optional[str] = Field(None, description="Crop variety")
    area_allocated: float = Field(..., gt=0, description="Area in hectares")
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    irrigation_method: Optional[str] = None
    expected_yield: Optional[float] = Field(None, description="Expected yield in tonnes")
    season: str = Field(..., description="Growing season, e.g., 2024/2025")


class HistoricalYield(BaseModel):
    """Historical yield data"""
    season: str
    crop_name: str
    area: float
    actual_yield: float
    success_notes: Optional[str] = None



# ============================================================
# MAIN FARMER MODELS
# ============================================================
class FarmerBase(BaseModel):
    """Base farmer information"""
    personal_info: PersonalInfo
    permanent_address: Address
    farm_address: Optional[Address] = Field(
        None, 
        description="Farm address if different from permanent address"
    )
    land_parcels: List[LandParcel] = []
    current_crops: List[Crop] = []
    historical_yields: List[HistoricalYield] = []
    future_planning: Optional[str] = Field(None, description="Future farming plans")
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
    permanent_address: Optional[Address] = None
    farm_address: Optional[Address] = None
    farm_details: Optional[FarmDetails] = None
    next_of_kin_name: Optional[str] = None
    next_of_kin_phone: Optional[str] = None
    land_parcels: Optional[List[LandParcel]] = None
    current_crops: Optional[List[Crop]] = None
    historical_yields: Optional[List[HistoricalYield]] = None
    future_planning: Optional[str] = None
    registration_status: Optional[RegistrationStatus] = None
    notes: Optional[str] = None
    last_modified_by: Optional[str] = None
    updated_at: Optional[datetime] = None


class Farmer(FarmerBase):
    """Complete farmer model with database fields"""
    id: Optional[PyObjectId] = Field(None, alias="_id", description="MongoDB ObjectId")
    farmer_id: str = Field(..., description="Unique farmer identifier (e.g., ZM000001)")
    qr_code: str = Field(..., description="QR code identifier")
    assigned_chief: Optional[str] = Field(None, description="Assigned chief ID")
    registration_status: str = Field(
        default="pending", 
        description="Registration status: pending, verified, approved"
    )
    verification_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="Operator who created record")
    verified_by: Optional[str] = Field(None, description="Admin who verified record")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        },
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "farmer_id": "ZM000001",
                "qr_code": "QR12345678AB",
                "personal_info": {
                    "first_name": "John",
                    "last_name": "Mwanza",
                    "phone_primary": "+260-97-1234567",
                    "email": "john.mwanza@example.com",
                    "date_of_birth": "1985-03-15",
                    "gender": "male",
                    "nrc_number": "123456/12/1"
                },
                "permanent_address": {
                    "street_village": "Kanyama Village",
                    "district": "Chibombo",
                    "province": "Central",
                    "chiefdom": "Chief Chitanda",
                    "gps_coordinates": {
                        "latitude": -14.7167,
                        "longitude": 28.4333
                    }
                },
                "registration_status": "verified"
            }
        }
    )


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


class FarmerResponse(BaseModel):
    """API response schema for farmer"""
    id: str = Field(..., description="Farmer ObjectId as string")
    farmer_id: str
    qr_code: str
    personal_info: PersonalInfo
    permanent_address: Address
    farm_address: Optional[Address] = None
    assigned_chief: Optional[str] = None
    registration_status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat()
        }
    )


class FarmerListResponse(BaseModel):
    """Paginated list response"""
    total: int
    page: int
    page_size: int
    farmers: List[FarmerResponse]
