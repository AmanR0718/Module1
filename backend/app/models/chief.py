"""
backend/app/models/chief.py
Pydantic model for Chief collection.
"""

"""
Chief model with proper Pydantic v2 configuration
"""
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from datetime import datetime


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic v2"""
    
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema(
            [
                core_schema.is_instance_schema(ObjectId),
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x)
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{24}$",
            "examples": ["507f1f77bcf86cd799439011"],
        }

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError(f"Invalid ObjectId: {v}")


class ContactInfo(BaseModel):
    """Contact information for a chief"""
    phone_primary: Optional[str] = Field(None, description="Primary phone number")
    phone_alternate: Optional[str] = Field(None, description="Alternate phone number")
    email: Optional[str] = Field(None, description="Email address")


class JurisdictionalBoundary(BaseModel):
    """Geographic boundaries of chiefdom"""
    type: str = Field(default="Polygon", description="GeoJSON type")
    coordinates: List[List[List[float]]] = Field(
        ..., 
        description="GeoJSON coordinates [longitude, latitude]"
    )


class ChiefBase(BaseModel):
    """Base chief information"""
    chief_name: str = Field(..., description="Name of the chief")
    title: str = Field(..., description="Traditional title")
    province: str = Field(..., description="Province name")
    district: str = Field(..., description="District name")
    chiefdom: str = Field(..., description="Chiefdom/Traditional area name")
    tribal_affiliation: Optional[str] = Field(None, description="Tribal group")
    contact_info: Optional[ContactInfo] = None
    jurisdictional_boundaries: Optional[JurisdictionalBoundary] = None


class ChiefCreate(ChiefBase):
    """Schema for creating a new chief"""
    pass


class ChiefUpdate(BaseModel):
    """Schema for updating chief information"""
    chief_name: Optional[str] = None
    title: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    chiefdom: Optional[str] = None
    tribal_affiliation: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
    jurisdictional_boundaries: Optional[JurisdictionalBoundary] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "chief_name": "Chief Chitambo",
                "contact_info": {
                    "phone_primary": "+260-97-1234567",
                    "email": "chief@example.com"
                }
            }
        }
    )


class Chief(ChiefBase):
    """Complete chief model with database fields"""
    id: Optional[PyObjectId] = Field(None, alias="_id", description="MongoDB ObjectId")
    chief_id: str = Field(..., description="Unique chief identifier")
    status: str = Field(default="active", description="Chief status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        },
        json_schema_extra={
            "example": {
                "_id": "507f1f77bcf86cd799439011",
                "chief_id": "ZM-CHIEF-001",
                "chief_name": "Chief Chitambo",
                "title": "Senior Chief",
                "province": "Central",
                "district": "Serenje",
                "chiefdom": "Chitambo",
                "tribal_affiliation": "Bemba",
                "status": "active",
                "contact_info": {
                    "phone_primary": "+260-97-1234567",
                    "email": "chief.chitambo@example.com"
                }
            }
        }
    )


class ChiefResponse(BaseModel):
    """API response schema for chief"""
    id: str = Field(..., description="Chief ObjectId as string")
    chief_id: str
    chief_name: str
    title: str
    province: str
    district: str
    chiefdom: str
    tribal_affiliation: Optional[str] = None
    contact_info: Optional[ContactInfo] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "chief_id": "ZM-CHIEF-001",
                "chief_name": "Chief Chitambo",
                "title": "Senior Chief",
                "province": "Central",
                "district": "Serenje",
                "chiefdom": "Chitambo",
                "tribal_affiliation": "Bemba",
                "status": "active",
                "created_at": "2025-10-18T06:00:00",
                "updated_at": "2025-10-18T06:00:00"
            }
        }
    )