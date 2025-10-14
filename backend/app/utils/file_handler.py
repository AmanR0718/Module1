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
