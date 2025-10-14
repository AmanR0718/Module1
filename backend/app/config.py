from pydantic_settings import BaseSettings
from pydantic import field_validator
from pydantic import Field
from typing import List, Union
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Zambian Farmer Support System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
   
    # MongoDB
    MONGODB_URL: str = "mongodb://admin:Admin123@mongodb:27017/"
    MONGODB_DB_NAME: str = "zambian_farmers"
   
    # JWT
    JWT_SECRET_KEY: str = "YourSuperSecureJWTKeyForZambianFarmersSystem2025"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
   
    # Security
    AES_ENCRYPTION_KEY: str = "YourAES256EncryptionKeyForSensitiveData2025"
   
    # CORS - Can accept both CSV string and List
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "http://localhost:8000",
        "http://10.169.131.102:3000",
        "http://10.169.131.102:19006",
        "http://10.169.131.102:8000",
    ]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_origins(cls, v):
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if isinstance(v, str):
            # Handle empty string
            if not v or v.strip() == "":
                return [
                    "http://localhost:3000",
                    "http://localhost:19006",
                    "http://localhost:8000",
                ]
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
   
    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 10
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf"}
   
    # Performance
    PROFILE_LOAD_TIMEOUT: int = 2
    SEARCH_TIMEOUT: int = 1
    REPORT_TIMEOUT: int = 5
   
    class Config:
        env_file = ".env"
        case_sensitive = True
        env_file_encoding = 'utf-8'

settings = Settings()

# Create upload directory if not exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)