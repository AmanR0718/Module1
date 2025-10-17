"""
backend/app/services/farmer_service.py
FarmerService — Core business logic for farmer validation, registration, and analytics.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import HTTPException, status
from app.utils.validators import (
    validate_phone_number,
    validate_nrc_number,
    validate_gps_coordinates,
    validate_age,
    validate_land_area,
)
from app.utils.security import encrypt_sensitive_data
import logging

logger = logging.getLogger(__name__)


class FarmerService:
    def __init__(self, db):
        self.db = db

    # ============================================================
    # 🔹 Farmer ID Generation
    # ============================================================
    async def generate_farmer_id(self) -> str:
        """Generate a unique farmer ID in the format ZM000001."""
        count = await self.db.farmers.count_documents({})
        farmer_id = f"ZM{count + 1:06d}"

        # Ensure uniqueness in edge cases
        while await self.db.farmers.find_one({"farmer_id": farmer_id}):
            count += 1
            farmer_id = f"ZM{count + 1:06d}"

        logger.info(f"Generated Farmer ID: {farmer_id}")
        return farmer_id

    # ============================================================
    # 🔹 Farmer Data Validation
    # ============================================================
    async def validate_farmer_data(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate farmer registration payload fields:
        - NRC format
        - Phone numbers
        - Age check (18+)
        - GPS coordinates
        - Duplicates (NRC/phone)
        - Land area
        Raises HTTPException if any validation fails.
        """
        errors: List[str] = []

        personal_info = farmer_data.get("personal_info", {})
        address = farmer_data.get("address", {})
        land_parcels = farmer_data.get("land_parcels", [])

        # ----------------------------
        # Phone validation
        # ----------------------------
        phone_primary = personal_info.get("phone_primary")
        if phone_primary and not validate_phone_number(phone_primary):
            errors.append("Invalid primary phone number format")

        phone_secondary = personal_info.get("phone_secondary")
        if phone_secondary and not validate_phone_number(phone_secondary):
            errors.append("Invalid secondary phone number format")

        # ----------------------------
        # Age validation
        # ----------------------------
        dob = personal_info.get("date_of_birth")
        if dob and not validate_age(dob):
            errors.append("Farmer must be at least 18 years old")

        # ----------------------------
        # NRC validation & duplication
        # ----------------------------
        nrc_number = farmer_data.get("nrc_number")
        if nrc_number:
            if not validate_nrc_number(nrc_number):
                errors.append("Invalid NRC number format")
            else:
                encrypted_nrc = encrypt_sensitive_data(nrc_number)
                existing_nrc = await self.db.farmers.find_one({"nrc_number": encrypted_nrc})
                if existing_nrc:
                    errors.append("NRC number already registered")

        # ----------------------------
        # Duplicate phone check
        # ----------------------------
        if phone_primary:
            existing_phone = await self.db.farmers.find_one(
                {"personal_info.phone_primary": phone_primary}
            )
            if existing_phone:
                errors.append("Primary phone number already registered")

        # ----------------------------
        # GPS validation
        # ----------------------------
        gps_lat = address.get("gps_latitude")
        gps_lon = address.get("gps_longitude")
        if gps_lat and gps_lon and not validate_gps_coordinates(gps_lat, gps_lon):
            errors.append("GPS coordinates outside Zambia boundaries")

        # ----------------------------
        # Land parcel validation
        # ----------------------------
        for idx, parcel in enumerate(land_parcels):
            area = parcel.get("total_area")
            if area and not validate_land_area(area):
                errors.append(f"Invalid land area for parcel {idx + 1}")

            parcel_gps = parcel.get("gps_coordinates", {})
            lat, lon = parcel_gps.get("latitude"), parcel_gps.get("longitude")
            if lat and lon and not validate_gps_coordinates(lat, lon):
                errors.append(f"Invalid GPS coordinates for parcel {idx + 1}")

        # ----------------------------
        # Raise error if validation fails
        # ----------------------------
        if errors:
            logger.warning(f"Farmer data validation failed: {errors}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Validation failed", "errors": errors},
            )

        logger.info("Farmer data validated successfully.")
        return {"valid": True, "errors": []}

    # ============================================================
    # 🔹 Assign Chief by Geolocation
    # ============================================================
    async def assign_chief(self, gps_coordinates: Dict[str, float]) -> Optional[str]:
        """
        Assign a chief automatically based on GPS coordinates.
        Uses MongoDB geospatial query to find nearest chief within 50 km radius.
        """
        latitude = gps_coordinates.get("latitude")
        longitude = gps_coordinates.get("longitude")

        if not latitude or not longitude:
            return None

        chief = await self.db.chiefs.find_one(
            {
                "palace_location": {
                    "$near": {
                        "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                        "$maxDistance": 50000,  # 50 km
                    }
                }
            }
        )

        if chief:
            logger.info(f"Assigned Chief: {chief.get('chief_name')}")
        return chief.get("chief_name") if chief else None

    # ============================================================
    # 🔹 Farmer Statistics (Analytics Dashboard)
    # ============================================================
    async def get_farmer_statistics(self, filters: Optional[Dict] = None) -> Dict:
        """
        Generate farmer statistics for dashboards.
        Includes:
        - Total farmers
        - Status breakdown
        - Province distribution
        - Crop statistics
        """
        query = filters or {}

        total_farmers = await self.db.farmers.count_documents(query)

        # Status breakdown
        status_stats = await self.db.farmers.aggregate(
            [
                {"$match": query},
                {"$group": {"_id": "$registration_status", "count": {"$sum": 1}}},
            ]
        ).to_list(None)

        # Province distribution
        province_stats = await self.db.farmers.aggregate(
            [
                {"$match": query},
                {"$group": {"_id": "$address.province", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
            ]
        ).to_list(None)

        # Crop statistics
        crop_stats = await self.db.farmers.aggregate(
            [
                {"$match": query},
                {"$unwind": {"path": "$farm_details.crops_grown", "preserveNullAndEmptyArrays": False}},
                {"$group": {"_id": "$farm_details.crops_grown", "farmers": {"$sum": 1}}},
                {"$sort": {"farmers": -1}},
            ]
        ).to_list(None)

        return {
            "total_farmers": total_farmers,
            "status_breakdown": status_stats,
            "province_distribution": province_stats,
            "crop_statistics": crop_stats,
        }
