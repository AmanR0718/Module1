from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.user import UserInDB
from app.routes.auth import get_current_active_user, require_role
from app.models.user import UserRole
from app.services.sync_service import SyncService
from app.database import get_database
from pydantic import BaseModel

router = APIRouter()

class SyncRequest(BaseModel):
    farmers: List[Dict[str, Any]]
    last_sync: Optional[datetime] = None

class SyncResponse(BaseModel):
    total: int
    successful: int
    failed: int
    results: List[Dict[str, Any]]
    errors: List[Dict[str, Any]]

@router.post("/batch", response_model=SyncResponse)
async def sync_batch_farmers(
    sync_request: SyncRequest,
    current_user: UserInDB = Depends(require_role([UserRole.ADMIN, UserRole.OPERATOR]))
):
    """Sync batch of farmers from mobile app"""
    db = get_database()
    sync_service = SyncService(db)
    
    result = await sync_service.batch_sync_farmers(
        sync_request.farmers,
        str(current_user.id)
    )
    
    return result

@router.get("/status")
async def get_sync_status(
    last_sync: datetime,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get sync status and pending updates"""
    db = get_database()
    sync_service = SyncService(db)
    
    status = await sync_service.get_sync_status(
        str(current_user.id),
        last_sync
    )
    
    return status


# ============================================
# File: backend/app/routes/reports.py
# ============================================
from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from app.models.user import UserInDB
from app.routes.auth import get_current_active_user
from app.services.report_service import ReportService
from app.database import get_database

router = APIRouter()

@router.get("/registration")
async def get_registration_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    province: Optional[str] = None,
    district: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate registration statistics report"""
    db = get_database()
    report_service = ReportService(db)
    
    report = await report_service.generate_registration_report(
        start_date, end_date, province, district
    )
    
    return report

@router.get("/crops")
async def get_crop_report(
    province: Optional[str] = None,
    district: Optional[str] = None,
    season: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate crop cultivation report"""
    db = get_database()
    report_service = ReportService(db)
    
    report = await report_service.generate_crop_report(
        province, district, season
    )
    
    return report

@router.get("/land-usage")
async def get_land_usage_report(
    province: Optional[str] = None,
    district: Optional[str] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate land usage report"""
    db = get_database()
    report_service = ReportService(db)
    
    report = await report_service.generate_land_usage_report(
        province, district
    )
    
    return report

@router.get("/operator-performance")
async def get_operator_performance_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate operator performance report"""
    db = get_database()
    report_service = ReportService(db)
    
    report = await report_service.generate_operator_performance_report(
        start_date, end_date
    )
    
    return report


# ============================================
# File: backend/app/utils/file_handler.py
# ============================================
import os
import aiofiles
from fastapi import UploadFile, HTTPException, status
from app.config import settings
from typing import Optional
import hashlib
from datetime import datetime

class FileHandler:
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.allowed_extensions = settings.ALLOWED_EXTENSIONS
        self.max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    
    def validate_file(self, file: UploadFile) -> bool:
        """Validate file type and size"""
        # Check extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed: {self.allowed_extensions}"
            )
        
        return True
    
    def generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(original_filename)[1]
        hash_suffix = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        
        return f"{prefix}_{timestamp}_{hash_suffix}{ext}"
    
    async def save_file(
        self, 
        file: UploadFile, 
        folder: str, 
        prefix: str = ""
    ) -> str:
        """Save uploaded file"""
        self.validate_file(file)
        
        # Create folder if not exists
        folder_path = os.path.join(self.upload_dir, folder)
        os.makedirs(folder_path, exist_ok=True)
        
        # Generate unique filename
        filename = self.generate_filename(file.filename, prefix)
        file_path = os.path.join(folder_path, filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            
            # Check file size
            if len(content) > self.max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
                )
            
            await out_file.write(content)
        
        return file_path
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
