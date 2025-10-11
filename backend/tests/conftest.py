import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.main import app
from app.database import get_database
from fastapi.testclient import TestClient

# Test database
TEST_MONGODB_URL = "mongodb://admin:password123@localhost:27017/"
TEST_DB_NAME = "zambian_farmers_test"

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """Create test database"""
    client = AsyncIOMotorClient(TEST_MONGODB_URL)
    db = client[TEST_DB_NAME]
    
    yield db
    
    # Cleanup
    await client.drop_database(TEST_DB_NAME)
    client.close()

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
async def admin_token(client):
    """Get admin authentication token"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@zambian-farmers.zm",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]