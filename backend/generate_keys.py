import secrets
import base64
from cryptography.fernet import Fernet

# JWT: 32+ chars URL-safe
jwt_secret = secrets.token_urlsafe(32)
print(f"JWT_SECRET_KEY={jwt_secret}")

# AES: 32-byte Fernet key (base64)
aes_key = Fernet.generate_key().decode()
print(f"AES_KEY={aes_key}")