from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Zambian Farmer Support System"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # MongoDB
    MONGODB_URL: str = "mongodb://admin:password123@mongodb:27017/"
    MONGODB_DB_NAME: str = "zambian_farmers"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Security
    AES_ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here!!"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:19006",
        "exp://192.168.1.1:19000"
    ]
    
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

settings = Settings()

# Create upload directory if not exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)