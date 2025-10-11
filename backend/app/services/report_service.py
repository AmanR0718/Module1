from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.database import get_database

class ReportService:
    def __init__(self, db):
        self.db = db
    
    async def generate_registration_report(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        province: Optional[str] = None,
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate farmer registration statistics report"""
        
        # Build query
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        if province:
            query["address.province"] = province
        if district:
            query["address.district"] = district
        
        # Total registrations
        total = await self.db.farmers.count_documents(query)
        
        # Daily registrations (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        daily_pipeline = [
            {"$match": {**query, "created_at": {"$gte": thirty_days_ago}}},
            {"$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}}
        ]
        daily_stats = await self.db.farmers.aggregate(daily_pipeline).to_list(None)
        
        # Status breakdown
        status_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$registration_status",
                "count": {"$sum": 1}
            }}
        ]
        status_stats = await self.db.farmers.aggregate(status_pipeline).to_list(None)
        
        # Gender distribution
        gender_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$personal_info.gender",
                "count": {"$sum": 1}
            }}
        ]
        gender_stats = await self.db.farmers.aggregate(gender_pipeline).to_list(None)
        
        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "total_registrations": total,
            "daily_registrations": daily_stats,
            "status_breakdown": status_stats,
            "gender_distribution": gender_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_crop_report(
        self,
        province: Optional[str] = None,
        district: Optional[str] = None,
        season: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate crop cultivation report"""
        
        query = {}
        if province:
            query["address.province"] = province
        if district:
            query["address.district"] = district
        
        # Crop statistics
        crop_pipeline = [
            {"$match": query},
            {"$unwind": "$current_crops"},
        ]
        
        if season:
            crop_pipeline.append({
                "$match": {"current_crops.season": season}
            })
        
        crop_pipeline.extend([
            {"$group": {
                "_id": "$current_crops.crop_name",
                "total_area": {"$sum": "$current_crops.area_allocated"},
                "farmers_count": {"$sum": 1},
                "avg_area_per_farmer": {"$avg": "$current_crops.area_allocated"},
                "total_estimated_yield": {"$sum": "$current_crops.estimated_yield"}
            }},
            {"$sort": {"total_area": -1}}
        ])
        
        crop_stats = await self.db.farmers.aggregate(crop_pipeline).to_list(None)
        
        # Irrigation method distribution
        irrigation_pipeline = [
            {"$match": query},
            {"$unwind": "$current_crops"},
            {"$group": {
                "_id": "$current_crops.irrigation_method",
                "count": {"$sum": 1}
            }}
        ]
        irrigation_stats = await self.db.farmers.aggregate(irrigation_pipeline).to_list(None)
        
        return {
            "filters": {
                "province": province,
                "district": district,
                "season": season
            },
            "crop_statistics": crop_stats,
            "irrigation_distribution": irrigation_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_land_usage_report(
        self,
        province: Optional[str] = None,
        district: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate land usage and ownership report"""
        
        query = {}
        if province:
            query["address.province"] = province
        if district:
            query["address.district"] = district
        
        # Total land area
        total_pipeline = [
            {"$match": query},
            {"$unwind": "$land_parcels"},
            {"$group": {
                "_id": None,
                "total_area": {"$sum": "$land_parcels.total_area"},
                "parcels_count": {"$sum": 1},
                "avg_parcel_size": {"$avg": "$land_parcels.total_area"}
            }}
        ]
        total_stats = await self.db.farmers.aggregate(total_pipeline).to_list(None)
        
        # Ownership distribution
        ownership_pipeline = [
            {"$match": query},
            {"$unwind": "$land_parcels"},
            {"$group": {
                "_id": "$land_parcels.ownership_type",
                "count": {"$sum": 1},
                "total_area": {"$sum": "$land_parcels.total_area"}
            }}
        ]
        ownership_stats = await self.db.farmers.aggregate(ownership_pipeline).to_list(None)
        
        # Soil type distribution
        soil_pipeline = [
            {"$match": query},
            {"$unwind": "$land_parcels"},
            {"$group": {
                "_id": "$land_parcels.soil_type",
                "count": {"$sum": 1},
                "total_area": {"$sum": "$land_parcels.total_area"}
            }}
        ]
        soil_stats = await self.db.farmers.aggregate(soil_pipeline).to_list(None)
        
        # Land type (irrigated vs non-irrigated)
        land_type_pipeline = [
            {"$match": query},
            {"$unwind": "$land_parcels"},
            {"$group": {
                "_id": "$land_parcels.land_type",
                "count": {"$sum": 1},
                "total_area": {"$sum": "$land_parcels.total_area"}
            }}
        ]
        land_type_stats = await self.db.farmers.aggregate(land_type_pipeline).to_list(None)
        
        return {
            "filters": {
                "province": province,
                "district": district
            },
            "total_statistics": total_stats[0] if total_stats else {},
            "ownership_distribution": ownership_stats,
            "soil_type_distribution": soil_stats,
            "land_type_distribution": land_type_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def generate_operator_performance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Generate operator performance metrics"""
        
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        
        # Registrations per operator
        operator_pipeline = [
            {"$match": query},
            {"$group": {
                "_id": "$created_by",
                "registrations": {"$sum": 1},
                "verified": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$registration_status", "verified"]},
                            1,
                            0
                        ]
                    }
                }
            }},
            {"$sort": {"registrations": -1}}
        ]
        operator_stats = await self.db.farmers.aggregate(operator_pipeline).to_list(None)
        
        # Enrich with operator details
        enriched_stats = []
        for stat in operator_stats:
            operator = await self.db.users.find_one({"_id": stat["_id"]})
            if operator:
                enriched_stats.append({
                    "operator_id": stat["_id"],
                    "operator_name": operator.get("full_name"),
                    "total_registrations": stat["registrations"],
                    "verified_registrations": stat["verified"],
                    "verification_rate": (stat["verified"] / stat["registrations"] * 100) if stat["registrations"] > 0 else 0
                })
        
        return {
            "period": {
                "start": start_date.isoformat() if start_date else None,
                "end": end_date.isoformat() if end_date else None
            },
            "operator_performance": enriched_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
