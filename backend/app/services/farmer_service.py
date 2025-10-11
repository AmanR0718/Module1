from typing import Optional, Dict, Any
from datetime import datetime
from app.utils.validators import (
    validate_phone_number,
    validate_nrc_number,
    validate_gps_coordinates,
    validate_age,
    validate_land_area
)
from fastapi import HTTPException, status

class FarmerService:
    def __init__(self, db):
        self.db = db
    
    async def generate_farmer_id(self) -> str:
        """Generate unique farmer ID in format ZM000001"""
        # Get count of existing farmers
        count = await self.db.farmers.count_documents({})
        farmer_id = f"ZM{count + 1:06d}"
        
        # Ensure uniqueness
        while await self.db.farmers.find_one({"farmer_id": farmer_id}):
            count += 1
            farmer_id = f"ZM{count + 1:06d}"
        
        return farmer_id
    
    async def validate_farmer_data(self, farmer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate farmer registration data"""
        errors = []
        
        # Validate personal information
        personal_info = farmer_data.get("personal_info", {})
        
        # Phone number validation
        phone_primary = personal_info.get("phone_primary")
        if phone_primary and not validate_phone_number(phone_primary):
            errors.append("Invalid primary phone number format")
        
        phone_alternate = personal_info.get("phone_alternate")
        if phone_alternate and not validate_phone_number(phone_alternate):
            errors.append("Invalid alternate phone number format")
        
        # Age validation
        dob = personal_info.get("date_of_birth")
        if dob and not validate_age(dob):
            errors.append("Farmer must be at least 18 years old")
        
        # NRC validation
        nrc_number = farmer_data.get("nrc_number")
        if nrc_number and not validate_nrc_number(nrc_number):
            errors.append("Invalid NRC number format")
        
        # Check for duplicate NRC
        if nrc_number:
            existing = await self.db.farmers.find_one({"nrc_number": nrc_number})
            if existing:
                errors.append("NRC number already registered")
        
        # Check for duplicate phone
        if phone_primary:
            existing = await self.db.farmers.find_one({
                "personal_info.phone_primary": phone_primary
            })
            if existing:
                errors.append("Phone number already registered")
        
        # Validate GPS coordinates
        address = farmer_data.get("address", {})
        gps = address.get("gps_coordinates", {})
        if gps:
            lat = gps.get("latitude")
            lon = gps.get("longitude")
            if lat and lon and not validate_gps_coordinates(lat, lon):
                errors.append("GPS coordinates outside Zambia boundaries")
        
        # Validate land parcels
        land_parcels = farmer_data.get("land_parcels", [])
        for idx, parcel in enumerate(land_parcels):
            area = parcel.get("total_area")
            if area and not validate_land_area(area):
                errors.append(f"Invalid land area for parcel {idx + 1}")
            
            # Validate land GPS
            parcel_gps = parcel.get("gps_coordinates", {})
            if parcel_gps:
                lat = parcel_gps.get("latitude")
                lon = parcel_gps.get("longitude")
                if lat and lon and not validate_gps_coordinates(lat, lon):
                    errors.append(f"Invalid GPS coordinates for parcel {idx + 1}")
        
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Validation failed", "errors": errors}
            )
        
        return {"valid": True, "errors": []}
    
    async def assign_chief(self, gps_coordinates: Dict[str, float]) -> Optional[str]:
        """Assign chief based on GPS coordinates"""
        latitude = gps_coordinates.get("latitude")
        longitude = gps_coordinates.get("longitude")
        
        if not latitude or not longitude:
            return None
        
        # Find nearest chief using geospatial query
        chief = await self.db.chiefs.find_one({
            "palace_location": {
                "$near": {
                    "$geometry": {
                        "type": "Point",
                        "coordinates": [longitude, latitude]
                    },
                    "$maxDistance": 50000  # 50km radius
                }
            }
        })
        
        return chief.get("chief_name") if chief else None
    
    async def get_farmer_statistics(self, filters: Optional[Dict] = None) -> Dict:
        """Get farmer statistics"""
        query = filters or {}
        
        total_farmers = await self.db.farmers.count_documents(query)
        
        # Get status breakdown
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$registration_status",
                "count": {"$sum": 1}
            }}
        ]
        status_stats = await self.db.farmers.aggregate(pipeline).to_list(None)
        
        # Get province distribution
        pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$address.province",
                "count": {"$sum": 1}
            }},
            {"$sort": {"count": -1}}
        ]
        province_stats = await self.db.farmers.aggregate(pipeline).to_list(None)
        
        # Get crop statistics
        pipeline = [
            {"$match": query},
            {"$unwind": "$current_crops"},
            {"$group": {
                "_id": "$current_crops.crop_name",
                "total_area": {"$sum": "$current_crops.area_allocated"},
                "farmers": {"$sum": 1}
            }},
            {"$sort": {"total_area": -1}}
        ]
        crop_stats = await self.db.farmers.aggregate(pipeline).to_list(None)
        
        return {
            "total_farmers": total_farmers,
            "status_breakdown": status_stats,
            "province_distribution": province_stats,
            "crop_statistics": crop_stats
        }
