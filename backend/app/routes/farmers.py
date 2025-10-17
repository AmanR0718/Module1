"""
backend/app/routes/chiefs.py
Chiefs Management Endpoints for Zambian Farmer Support System.
"""


from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
)
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime
from fastapi import UploadFile, File
from app.utils.file_handler import FileHandler
from app.models.chief import Chief
from app.models.user import UserInDB, UserRole
from app.database import get_database
from app.routes.auth import get_current_active_user, require_role

router = APIRouter(prefix="/api/chiefs", tags=["Chiefs"])
file_handler = FileHandler()



# ============================================================
# 🔹 Utility Function
# ============================================================
def format_chief(chief_doc: dict) -> Chief:
    """Convert MongoDB document to Chief model."""
    chief_doc["_id"] = str(chief_doc.get("_id"))
    return Chief(**chief_doc)


# ============================================================
# 🔹 Endpoints
# ============================================================
@router.get("/", response_model=List[Chief], status_code=status.HTTP_200_OK)
async def get_chiefs(
    province: Optional[str] = Query(None, description="Filter by province"),
    district: Optional[str] = Query(None, description="Filter by district"),
    active_only: bool = Query(False, description="Return only active chiefs"),
    skip: int = Query(0, ge=0, description="Pagination skip count"),
    limit: int = Query(100, le=500, description="Pagination limit"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Retrieve a list of chiefs with optional filters (province, district, active).
    """
    query = {}
    if province:
        query["province"] = province
    if district:
        query["district"] = district
    if active_only:
        query["is_active"] = True

    cursor = db.chiefs.find(query).skip(skip).limit(limit)
    chiefs = await cursor.to_list(length=limit)
    return [format_chief(ch) for ch in chiefs]


# ------------------------------------------------------------
@router.get("/provinces", status_code=status.HTTP_200_OK)
async def get_provinces(
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Retrieve a list of all provinces where chiefs exist.
    """
    provinces = await db.chiefs.distinct("province")
    return {"provinces": sorted(p for p in provinces if p)}


# ------------------------------------------------------------
@router.get("/districts", status_code=status.HTTP_200_OK)
async def get_districts(
    province: Optional[str] = Query(None, description="Province name for filtering"),
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Retrieve all districts, optionally filtered by a given province.
    """
    query = {"province": province} if province else {}
    districts = await db.chiefs.distinct("district", query)
    return {"districts": sorted(d for d in districts if d)}


# ------------------------------------------------------------
@router.get("/{chief_id}", response_model=Chief, status_code=status.HTTP_200_OK)
async def get_chief_by_id(
    chief_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Retrieve a single chief by their MongoDB ID.
    """
    if not ObjectId.is_valid(chief_id):
        raise HTTPException(status_code=400, detail="Invalid Chief ID format.")

    chief = await db.chiefs.find_one({"_id": ObjectId(chief_id)})
    if not chief:
        raise HTTPException(status_code=404, detail="Chief not found.")

    return format_chief(chief)


# ------------------------------------------------------------
@router.post("/", response_model=Chief, status_code=status.HTTP_201_CREATED)
async def create_chief(
    chief: Chief,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN])),
):
    """
    Create a new chief record (Admin only).
    """
    existing = await db.chiefs.find_one({
        "chief_name": chief.chief_name,
        "province": chief.province,
        "district": chief.district
    })
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Chief '{chief.chief_name}' already exists in {chief.district}, {chief.province}.",
        )

    chief_doc = chief.model_dump(by_alias=True)
    chief_doc["is_active"] = chief_doc.get("is_active", True)
    chief_doc["created_at"] = datetime.utcnow()
    chief_doc["updated_at"] = datetime.utcnow()
    chief_doc["created_by"] = current_user.email

    result = await db.chiefs.insert_one(chief_doc)
    chief_doc["_id"] = str(result.inserted_id)
    return Chief(**chief_doc)


# ------------------------------------------------------------
@router.put("/{chief_id}", response_model=Chief, status_code=status.HTTP_200_OK)
async def update_chief(
    chief_id: str,
    updated_chief: Chief,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN])),
):
    """
    Update a chief's information (Admin only).
    """
    if not ObjectId.is_valid(chief_id):
        raise HTTPException(status_code=400, detail="Invalid Chief ID format.")

    chief = await db.chiefs.find_one({"_id": ObjectId(chief_id)})
    if not chief:
        raise HTTPException(status_code=404, detail="Chief not found.")

    update_data = updated_chief.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    update_data["last_modified_by"] = current_user.email

    await db.chiefs.update_one({"_id": ObjectId(chief_id)}, {"$set": update_data})
    updated = await db.chiefs.find_one({"_id": ObjectId(chief_id)})
    return format_chief(updated)


# ------------------------------------------------------------
@router.delete("/{chief_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chief(
    chief_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN])),
):
    """
    Delete a chief record (Admin only).
    """
    if not ObjectId.is_valid(chief_id):
        raise HTTPException(status_code=400, detail="Invalid Chief ID format.")

    result = await db.chiefs.delete_one({"_id": ObjectId(chief_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chief not found.")
    return {"detail": "Chief deleted successfully."}


@router.post("/{farmer_id}/upload-photo")
async def upload_farmer_photo(farmer_id: str, file: UploadFile = File(...), db=Depends(get_database)):
    """Upload farmer photo."""
    saved_file = await file_handler.save_file(file, folder="photos", prefix=farmer_id)
    await db.farmers.update_one({"farmer_id": farmer_id}, {"$set": {"photo_path": saved_file["path"]}})
    return {"message": "Photo uploaded", "file": saved_file}

@router.post("/{farmer_id}/upload-id")
async def upload_farmer_id(farmer_id: str, file: UploadFile = File(...), db=Depends(get_database)):
    """Upload farmer ID document."""
    saved_file = await file_handler.save_file(file, folder="documents", prefix=farmer_id)
    await db.farmers.update_one({"farmer_id": farmer_id}, {"$set": {"id_document_path": saved_file["path"]}})
    return {"message": "ID document uploaded", "file": saved_file}