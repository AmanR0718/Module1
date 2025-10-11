#!/usr/bin/env python3
import secrets
import string

def generate_secret_key(length=64):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_aes_key():
    """Generate AES encryption key (32 bytes)"""
    return secrets.token_urlsafe(32)

if __name__ == "__main__":
    print("🔐 Generating secure keys for production...")
    print("")
    print("JWT_SECRET_KEY:")
    print(generate_secret_key())
    print("")
    print("AES_ENCRYPTION_KEY:")
    print(generate_aes_key())
    print("")
    print("⚠️  Save these keys securely and add them to your .env file")

