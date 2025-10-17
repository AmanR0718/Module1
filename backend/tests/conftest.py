"""
backend/tests/conftest.py
Pytest configuration for FastAPI integration + async MongoDB testing.
"""

import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.testclient import TestClient
from datetime import datetime
from jose import jwt

from app.main import app
from app.config import settings
from app.utils.security import get_password_hash, create_access_token
from app.database import get_database

# ============================================================
# 🔹 TEST DATABASE CONFIGURATION
# ============================================================
TEST_MONGODB_URL = "mongodb://admin:Admin123@localhost:27017/"
TEST_DB_NAME = "zambian_farmers_test"

# ============================================================
# 🔹 EVENT LOOP (ASYNC FIXTURE)
# ============================================================
@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# ============================================================
# 🔹 TEST DATABASE FIXTURE
# ============================================================
@pytest.fixture(scope="function")
async def test_db():
    """Create and yield a clean test MongoDB database."""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    db = client[TEST_DB_NAME]

    # Clear collections before each test
    for collection_name in await db.list_collection_names():
        await db[collection_name].delete_many({})

    yield db

    # Cleanup after tests
    await client.drop_database(TEST_DB_NAME)
    client.close()

# ============================================================
# 🔹 FASTAPI TEST CLIENT
# ============================================================
@pytest.fixture(scope="session")
def client():
    """Return FastAPI test client."""
    return TestClient(app)

# ============================================================
# 🔹 SEED ADMIN USER FIXTURE
# ============================================================
@pytest.fixture(scope="function", autouse=True)
async def seed_admin_user(test_db):
    """Insert a default admin user into test DB."""
    hashed_password = get_password_hash("admin123")
    await test_db.users.insert_one({
        "email": "admin@test.com",
        "full_name": "System Administrator",
        "role": "admin",
        "is_active": True,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })
    yield

# ============================================================
# 🔹 ADMIN TOKEN FIXTURE (JWT)
# ============================================================
@pytest.fixture(scope="function")
def admin_token() -> str:
    """Generate a valid JWT token for admin."""
    token_data = {
        "sub": "admin@test.com",
        "role": "admin",
        "user_id": "test_admin_id",
    }
    return create_access_token(token_data)

# ============================================================
# 🔹 AUTHENTICATED CLIENT
# ============================================================
@pytest.fixture(scope="function")
def auth_client(client, admin_token):
    """Return a client with Authorization header set."""
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client

# ============================================================
# 🔹 MOCKED DEPENDENCY OVERRIDE (OPTIONAL)
# ============================================================
@pytest.fixture(scope="function", autouse=True)
def override_get_database(test_db):
    """Override FastAPI dependency to use test DB."""
    async def _get_test_db():
        return test_db

    app.dependency_overrides[get_database] = _get_test_db
    yield
    app.dependency_overrides.clear()
