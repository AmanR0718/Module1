
from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile
from typing import List, Optional
from datetime import datetime
from app.models.farmer import (
    FarmerCreate, Farmer, FarmerUpdate, FarmerInDB, 
    RegistrationStatus
)
from app.models.user import UserInDB, UserRole
from app.routes.auth import get_current_active_user, require_role
from app.database import get_database
from app.services.farmer_service import FarmerService
from app.services.qr_service import QRCodeService
import os

router = APIRouter()

@router.post("/", response_model=Farmer, status_code=status.HTTP_201_CREATED)
async def create_farmer(
    farmer: FarmerCreate,
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Create new farmer registration"""
    db = get_database()
    farmer_service = FarmerService(db)
    qr_service = QRCodeService()
    
    # Generate unique farmer ID
    farmer_id = await farmer_service.generate_farmer_id()
    
    # Create farmer document
    farmer_dict = farmer.dict()
    farmer_dict.update({
        "farmer_id": farmer_id,
        "qr_code": "",  # Will be generated
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": str(current_user.id)
    })
    
    # Generate QR code
    qr_code_data = qr_service.generate_qr_data(farmer_id, farmer_dict)
    qr_image_path = qr_service.generate_qr_image(qr_code_data, farmer_id)
    
    farmer_dict["qr_code"] = qr_code_data
    farmer_dict["qr_code_image_path"] = qr_image_path
    
    # Insert into database
    result = await db.farmers.insert_one(farmer_dict)
    farmer_dict["_id"] = str(result.inserted_id)
    
    return Farmer(**farmer_dict)

@router.get("/", response_model=List[Farmer])
async def get_farmers(
    skip: int = 0,
    limit: int = 100,
    province: Optional[str] = None,
    district: Optional[str] = None,
    status: Optional[RegistrationStatus] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get list of farmers with filters"""
    db = get_database()
    query = {}
    
    # Apply filters
    if province:
        query["address.province"] = province
    if district:
        query["address.district"] = district
    if status:
        query["registration_status"] = status
    
    # Role-based filtering
    if current_user.role == UserRole.OPERATOR:
        if current_user.assigned_provinces:
            query["address.province"] = {"$in": current_user.assigned_provinces}
        if current_user.assigned_districts:
            query["address.district"] = {"$in": current_user.assigned_districts}
    
    cursor = db.farmers.find(query).skip(skip).limit(limit)
    farmers = await cursor.to_list(length=limit)
    
    return [Farmer(**farmer) for farmer in farmers]

@router.get("/{farmer_id}", response_model=Farmer)
async def get_farmer(
    farmer_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get farmer by ID"""
    db = get_database()
    farmer = await db.farmers.find_one({"farmer_id": farmer_id})
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Check operator permissions
    if current_user.role == UserRole.OPERATOR:
        if current_user.assigned_provinces:
            if farmer["address"]["province"] not in current_user.assigned_provinces:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this farmer's data"
                )
    
    return Farmer(**farmer)

@router.put("/{farmer_id}", response_model=Farmer)
async def update_farmer(
    farmer_id: str,
    farmer_update: FarmerUpdate,
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Update farmer information"""
    db = get_database()
    
    # Find existing farmer
    existing_farmer = await db.farmers.find_one({"farmer_id": farmer_id})
    if not existing_farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    # Update only provided fields
    update_data = farmer_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow()
    
    await db.farmers.update_one(
        {"farmer_id": farmer_id},
        {"$set": update_data}
    )
    
    # Get updated farmer
    updated_farmer = await db.farmers.find_one({"farmer_id": farmer_id})
    return Farmer(**updated_farmer)

@router.delete("/{farmer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_farmer(
    farmer_id: str,
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN]))
):
    """Delete farmer (Admin only)"""
    db = get_database()
    result = await db.farmers.delete_one({"farmer_id": farmer_id})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )

@router.get("/search/by-phone")
async def search_by_phone(
    phone: str = Query(..., description="Phone number to search"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Search farmer by phone number"""
    db = get_database()
    farmer = await db.farmers.find_one({
        "personal_info.phone_primary": phone
    })
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    return Farmer(**farmer)

@router.get("/search/by-nrc")
async def search_by_nrc(
    nrc: str = Query(..., description="NRC number to search"),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Search farmer by NRC number"""
    db = get_database()
    farmer = await db.farmers.find_one({"nrc_number": nrc})
    
    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    return Farmer(**farmer)

@router.post("/{farmer_id}/verify")
async def verify_farmer(
    farmer_id: str,
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Verify farmer registration"""
    db = get_database()
    
    result = await db.farmers.update_one(
        {"farmer_id": farmer_id},
        {
            "$set": {
                "registration_status": RegistrationStatus.VERIFIED,
                "verified_by": str(current_user.id),
                "verified_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer not found"
        )
    
    return {"message": "Farmer verified successfully"}

@router.post("/{farmer_id}/upload-document")
async def upload_document(
    farmer_id: str,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type of document"),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Upload farmer document"""
    from app.config import settings
    import aiofiles
    
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, farmer_id)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, f"{document_type}_{file.filename}")
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Update farmer document record
    db = get_database()
    await db.farmers.update_one(
        {"farmer_id": farmer_id},
        {
            "$push": {
                "identification_documents": {
                    "doc_type": document_type,
                    "file_path": file_path,
                    "uploaded_at": datetime.utcnow()
                }
            }
        }
    )
    
    return {"message": "Document uploaded successfully", "file_path": file_path}