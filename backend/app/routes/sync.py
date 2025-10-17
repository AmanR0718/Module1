"""
backend/app/routes/sync.py
Handles offline → online synchronization between mobile app and backend.
"""

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from typing import List, Dict, Any, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.models.user import UserInDB, UserRole
from app.routes.auth import get_current_active_user, require_role
from app.services.sync_service import SyncService
from app.core.database import get_database
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sync", tags=["Synchronization"])


# ============================================================
# 🔹 MODELS
# ============================================================
class SyncFarmer(BaseModel):
    """Farmer object received from mobile app."""
    farmer_id: str
    nrc_number: str
    personal_info: Dict[str, Any]
    address: Dict[str, Any]
    farm_details: Dict[str, Any]
    registration_status: Optional[str] = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class SyncRequest(BaseModel):
    """Batch sync request model."""
    farmers: List[SyncFarmer]
    last_sync: Optional[datetime] = Field(None, description="Last time the mobile app synced successfully")


class SyncResponse(BaseModel):
    """Response after sync operation."""
    total: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]
    server_timestamp: datetime


# ============================================================
# 🔹 SYNC ROUTES
# ============================================================

@router.post("/batch", response_model=SyncResponse, status_code=status.HTTP_200_OK)
async def sync_batch_farmers(
    sync_request: SyncRequest,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.EXTENSION_OFFICER])),
):
    """
    Synchronize a batch of farmers uploaded from the mobile app.
    This route:
    - Receives farmer data payloads.
    - Validates and encrypts sensitive fields.
    - Inserts new records or updates existing ones.
    - Returns success/failure results per record.
    """
    sync_service = SyncService(db)
    logger.info(f"Starting batch sync: {len(sync_request.farmers)} records from {current_user.email}")

    try:
        result = await sync_service.batch_sync_farmers(sync_request.farmers, str(current_user.id))
        result["server_timestamp"] = datetime.utcnow()
        return result
    except Exception as e:
        logger.error(f"Batch sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Batch synchronization failed")

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_sync_status(
    last_sync: Optional[datetime] = None,
    db: AsyncIOMotorDatabase = Depends(get_database),
    current_user: UserInDB = Depends(get_current_active_user),
):
    """
    Check what data has been updated since the last sync.
    Used by the mobile app to download incremental changes.
    """
    sync_service = SyncService(db)
    try:
        status = await sync_service.get_sync_status(str(current_user.id), last_sync)
        return status
    except Exception as e:
        logger.error(f"Error retrieving sync status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve sync status")

