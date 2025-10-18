"""
Common types and utilities for models
Shared across all Pydantic models to ensure consistency
"""
from typing import Any
from bson import ObjectId
from pydantic_core import core_schema
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue


class PyObjectId(ObjectId):
    """
    Custom ObjectId type for Pydantic v2
    Properly handles JSON schema generation for FastAPI OpenAPI docs
    
    Usage:
        from app.models.common import PyObjectId
        
        class MyModel(BaseModel):
            id: Optional[PyObjectId] = Field(None, alias="_id")
    """
    
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Define how Pydantic should validate this type.
        Accepts both ObjectId instances and valid ObjectId strings.
        """
        return core_schema.union_schema(
            [
                # If it's already an ObjectId, use it as is
                core_schema.is_instance_schema(ObjectId),
                # If it's a string, validate and convert it
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda x: str(x),
                return_schema=core_schema.str_schema(),
            ),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: core_schema.CoreSchema,
        handler: GetJsonSchemaHandler,
    ) -> JsonSchemaValue:
        """
        Define the JSON schema representation for OpenAPI documentation.
        Shows as a string with pattern validation in the docs.
        """
        return {
            "type": "string",
            "pattern": "^[0-9a-fA-F]{24}$",
            "examples": ["507f1f77bcf86cd799439011", "65f3e2b1c4a5d6e7f8a9b0c1"],
            "description": "MongoDB ObjectId as a 24-character hexadecimal string"
        }

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """
        Validate and convert input to ObjectId.
        
        Args:
            v: Value to validate (ObjectId or string)
            
        Returns:
            ObjectId instance
            
        Raises:
            ValueError: If string is not a valid ObjectId
            TypeError: If value is neither ObjectId nor string
        """
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            if ObjectId.is_valid(v):
                return ObjectId(v)
            raise ValueError(f"Invalid ObjectId format: {v}")
        raise TypeError(f"ObjectId expected, got {type(v).__name__}")

    @classmethod
    def __str__(cls) -> str:
        return "PyObjectId"


# Common model configuration for all database models
COMMON_MODEL_CONFIG = {
    "populate_by_name": True,
    "arbitrary_types_allowed": True,
    "json_encoders": {
        ObjectId: str,
    },
}


def generate_object_id() -> str:
    """
    Generate a new MongoDB ObjectId as a string
    
    Returns:
        24-character hexadecimal string
    """
    return str(ObjectId())