"""
backend/app/routes/farmer_stats.py
Provides summarized analytics of farmers.
"""

from fastapi import APIRouter, Depends
from app.routes.auth import get_current_active_user
from app.database import get_database

router = APIRouter(prefix="/api/farmers", tags=["Farmer Statistics"])


@router.get("/stats")
async def get_farmer_statistics(db=Depends(get_database), current_user=Depends(get_current_active_user)):
    """Return farmer count by province, gender, and status."""
    total = await db.farmers.count_documents({})
    active = await db.farmers.count_documents({"registration_status": "active"})
    pending = await db.farmers.count_documents({"registration_status": "pending"})

    pipeline = [
        {"$group": {"_id": "$address.province", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    province_stats = await db.farmers.aggregate(pipeline).to_list(None)

    gender_pipeline = [
        {"$group": {"_id": "$personal_info.gender", "count": {"$sum": 1}}}
    ]
    gender_stats = await db.farmers.aggregate(gender_pipeline).to_list(None)

    return {
        "total_farmers": total,
        "active_farmers": active,
        "pending_registrations": pending,
        "farmers_by_province": province_stats,
        "gender_distribution": gender_stats,
    }
