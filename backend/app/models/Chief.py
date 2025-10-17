"""
backend/app/models/chief.py
Pydantic model for Chief collection.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom type for MongoDB ObjectId fields."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Chief(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    chief_name: str = Field(..., description="Name of the Chief")
    tribal_affiliation: str = Field(..., description="Tribal group or ethnic affiliation")
    province: str = Field(..., description="Province name")
    district: str = Field(..., description="District name")
    chiefdom: str = Field(..., description="Chiefdom under governance")
    phone: Optional[str] = Field(None, description="Chief's contact number")
    email: Optional[str] = Field(None, description="Chief's email address")
    jurisdiction_boundaries: Optional[Dict[str, str]] = Field(
        None, description="Administrative boundaries (JSON object)"
    )
    palace_location: Optional[Dict[str, float]] = Field(
        None, description="GPS coordinates (latitude, longitude)"
    )
    is_active: bool = Field(default=True, description="Chief’s record active status")

    class Config:
        populate_by_name = True
        from_attributes = True  # Pydantic v2: allows conversion from ORM objects
