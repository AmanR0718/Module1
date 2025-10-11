from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.models.chief import Chief
from app.routes.auth import get_current_active_user
from app.database import get_database

router = APIRouter()

@router.get("/", response_model=List[Chief])
async def get_chiefs(
    province: Optional[str] = None,
    district: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user)
):
    """Get list of chiefs with filters"""
    db = get_database()
    query = {}
    
    if province:
        query["province"] = province
    if district:
        query["district"] = district
    
    cursor = db.chiefs.find(query).skip(skip).limit(limit)
    chiefs = await cursor.to_list(length=limit)
    
    return [Chief(**chief) for chief in chiefs]

@router.get("/provinces")
async def get_provinces(current_user = Depends(get_current_active_user)):
    """Get list of all provinces"""
    db = get_database()
    provinces = await db.chiefs.distinct("province")
    return {"provinces": sorted(provinces)}

@router.get("/districts")
async def get_districts(
    province: Optional[str] = Query(None),
    current_user = Depends(get_current_active_user)
):
    """Get list of districts, optionally filtered by province"""
    db = get_database()
    query = {"province": province} if province else {}
    districts = await db.chiefs.distinct("district", query)
    return {"districts": sorted(districts)}

@router.post("/", response_model=Chief)
async def create_chief(
    chief: Chief,
    current_user = Depends(get_current_active_user)
):
    """Create new chief entry (Admin only)"""
    db = get_database()
    chief_dict = chief.dict()
    
    result = await db.chiefs.insert_one(chief_dict)
    chief_dict["_id"] = str(result.inserted_id)
    
    return Chief(**chief_dict)
