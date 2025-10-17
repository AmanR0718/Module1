"""
backend/app/utils/file_handler.py
Utility for handling secure, asynchronous file uploads and deletions.
"""

import os
import aiofiles
import hashlib
import mimetypes
import logging
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from typing import Optional, Dict
from app.config import settings

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility class for managing file uploads, validation, and deletion."""

    def __init__(self):
        self.upload_dir = os.path.abspath(settings.UPLOAD_DIR)
        self.allowed_extensions = {ext.lower() for ext in settings.ALLOWED_EXTENSIONS}
        self.max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024  # MB → bytes

        # Ensure base upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)

    # ============================================================
    # 🔹 VALIDATION
    # ============================================================
    def validate_file(self, file: UploadFile) -> None:
        """Validate file extension and MIME type."""
        ext = os.path.splitext(file.filename)[1].lower()

        if ext not in self.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type '{ext}' not allowed. Allowed types: {self.allowed_extensions}",
            )

        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type or not mime_type.startswith(("image/", "application/pdf")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type '{mime_type}' for {file.filename}",
            )

    # ============================================================
    # 🔹 FILENAME GENERATION
    # ============================================================
    def generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename using timestamp + hash suffix."""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        ext = os.path.splitext(original_filename)[1]
        hash_suffix = hashlib.md5(original_filename.encode()).hexdigest()[:8]
        prefix_str = f"{prefix}_" if prefix else ""
        return f"{prefix_str}{timestamp}_{hash_suffix}{ext}"

    # ============================================================
    # 🔹 SAVE FILE
    # ============================================================
    async def save_file(self, file: UploadFile, folder: str, prefix: str = "") -> Dict[str, str]:
        """
        Save uploaded file asynchronously to server.
        Returns a dictionary with file metadata.
        """
        self.validate_file(file)

        # Create target folder if missing
        folder_path = os.path.join(self.upload_dir, folder)
        os.makedirs(folder_path, exist_ok=True)

        # Generate unique filename and normalized path
        filename = self.generate_filename(file.filename, prefix)
        file_path = os.path.join(folder_path, filename)
        normalized_path = os.path.normpath(file_path)

        try:
            file_size = 0
            async with aiofiles.open(normalized_path, "wb") as out_file:
                while chunk := await file.read(1024 * 1024):  # Stream 1MB chunks
                    file_size += len(chunk)
                    if file_size > self.max_size:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB",
                        )
                    await out_file.write(chunk)

            relative_path = os.path.relpath(normalized_path, self.upload_dir)
            logger.info(f"📁 Saved file: {relative_path} ({file_size / 1024:.2f} KB)")

            return {
                "filename": filename,
                "path": relative_path.replace("\\", "/"),  # Cross-platform compatibility
                "size_kb": round(file_size / 1024, 2),
                "uploaded_at": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ File upload failed for {file.filename}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"File upload failed: {str(e)}",
            )

    # ============================================================
    # 🔹 DELETE FILE
    # ============================================================
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from server storage."""
        try:
            abs_path = os.path.join(self.upload_dir, file_path)
            if os.path.exists(abs_path):
                os.remove(abs_path)
                logger.info(f"🗑️ Deleted file: {abs_path}")
                return True
            else:
                logger.warning(f"⚠️ File not found for deletion: {abs_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Error deleting file: {e}", exc_info=True)
            return False
