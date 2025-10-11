from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class LandOwnership(str, Enum):
    OWNED = "owned"
    LEASED = "leased"
    SHARED = "shared"

class LandType(str, Enum):
    IRRIGATED = "irrigated"
    NON_IRRIGATED = "non_irrigated"

class RegistrationStatus(str, Enum):
    DRAFT = "draft"
    PENDING_VERIFICATION = "pending_verification"
    VERIFIED = "verified"
    REJECTED = "rejected"

class GPSCoordinates(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
    captured_at: Optional[datetime] = None

class PersonalInfo(BaseModel):
    first_name: str
    last_name: str
    phone_primary: str
    phone_alternate: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: date
    gender: Gender
    
    @validator('phone_primary', 'phone_alternate')
    def validate_phone(cls, v):
        if v and not v.startswith('+260'):
            raise ValueError('Phone must start with +260 (Zambian format)')
        return v

class Address(BaseModel):
    province: str
    district: str
    chiefdom: Optional[str] = None
    village: str
    gps_coordinates: GPSCoordinates

class IdentificationDocument(BaseModel):
    doc_type: str  # NRC, Passport, etc.
    doc_number: str
    issue_date: Optional[date] = None
    expiry_date: Optional[date] = None
    file_path: Optional[str] = None
    verification_status: str = "pending"

class LandParcel(BaseModel):
    parcel_id: str
    total_area: float  # in hectares
    ownership_type: LandOwnership
    land_type: LandType
    soil_type: Optional[str] = None
    water_sources: Optional[List[str]] = []
    gps_coordinates: GPSCoordinates
    lease_details: Optional[dict] = None

class Crop(BaseModel):
    crop_name: str
    variety: Optional[str] = None
    area_allocated: float  # in hectares
    planting_date: Optional[date] = None
    expected_harvest_date: Optional[date] = None
    irrigation_method: Optional[str] = None
    estimated_yield: Optional[float] = None
    season: str  # e.g., "2024/2025"

class HistoricalData(BaseModel):
    year: int
    season: str
    crop_name: str
    area: float
    actual_yield: float
    notes: Optional[str] = None

class FarmerBase(BaseModel):
    personal_info: PersonalInfo
    address: Address
    nrc_number: str
    identification_documents: List[IdentificationDocument] = []
    land_parcels: List[LandParcel] = []
    current_crops: List[Crop] = []
    historical_data: List[HistoricalData] = []
    registration_status: RegistrationStatus = RegistrationStatus.DRAFT

class FarmerCreate(FarmerBase):
    pass

class FarmerUpdate(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    address: Optional[Address] = None
    land_parcels: Optional[List[LandParcel]] = None
    current_crops: Optional[List[Crop]] = None
    registration_status: Optional[RegistrationStatus] = None

class FarmerInDB(FarmerBase):
    id: str = Field(alias="_id")
    farmer_id: str  # Unique ID like ZM000001
    qr_code: str
    qr_code_image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    created_by: str  # User ID of operator
    verified_by: Optional[str] = None
    
    class Config:
        populate_by_name = True

class Farmer(FarmerBase):
    id: str
    farmer_id: str
    qr_code: str
    created_at: datetime
    updated_at: datetime