"""
backend/app/core/config.py
Zambian Farmer System — Centralized application settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, Field
from typing import List, Union
import os


class Settings(BaseSettings):
    # ============================================
    # 🔹 Application Info
    # ============================================
    APP_NAME: str = "Zambian Farmer Support System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    # ============================================
    # 🔹 MongoDB Configuration
    # ============================================
    MONGODB_URL: str = "mongodb://admin:Admin123@mongodb:27017/"
    MONGODB_DB_NAME: str = "zambian_farmers"

    # ============================================
    # 🔹 JWT Configuration
    # ============================================
    JWT_SECRET_KEY: str = "tt1eTajVweALvwxHqBGwVjNqScCjT4NoSd1-4q3edLk"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ============================================
    # 🔹 AES Encryption
    # ============================================
    AES_ENCRYPTION_KEY: str = "315741653158b40e3608bbe97704bb22"

    @field_validator("AES_ENCRYPTION_KEY")
    @classmethod
    def validate_aes_length(cls, v: str) -> str:
        """Ensure AES key length is 32 characters for AES-256."""
        if len(v) != 32:
            raise ValueError("AES_ENCRYPTION_KEY must be exactly 32 characters for AES-256 encryption.")
        return v

    # ============================================
    # 🔹 CORS Origins
    # Can be either a CSV string or a List[str]
    # ============================================
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "http://localhost:8000",
        "http://localhost:8081",
        "http://10.169.131.102:3000",
        "http://10.169.131.102:19006",
        "http://10.169.131.102:8000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list."""
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return []
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # ============================================
    # 🔹 File Uploads
    # ============================================
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set[str] = {".jpg", ".jpeg", ".png", ".pdf"}

    # ============================================
    # 🔹 Performance / Timeouts
    # ============================================
    PROFILE_LOAD_TIMEOUT: int = 2
    SEARCH_TIMEOUT: int = 1
    REPORT_TIMEOUT: int = 5

    # ============================================
    # 🔹 Logging
    # ============================================
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"

    # ============================================
    # 🔹 Redis (optional)
    # ============================================
    REDIS_URL: str = "redis://redis:6379/0"

    # ============================================
    # 🔹 Pydantic Settings Config
    # ============================================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instantiate global settings
settings = Settings()

# ============================================
# Ensure Upload & Log Directories Exist
# ============================================
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
