"""
backend/tests/test_farmers.py
Integration tests for Farmer API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ============================================================
# 🔹 FIXTURES
# ============================================================
@pytest.fixture
def sample_farmer_data():
    """Return a sample valid farmer payload."""
    return {
        "personal_info": {
            "first_name": "John",
            "last_name": "Tester",
            "phone_primary": "+260971234567",
            "date_of_birth": "1985-05-15",
            "gender": "male",
        },
        "address": {
            "province": "Central",
            "district": "Chibombo",
            "village": "Test Village",
            "gps_latitude": -14.7167,
            "gps_longitude": 28.4333,
        },
        "nrc_number": "123456/12/1",
        "farm_details": {
            "farm_size_hectares": 5.5,
            "crops_grown": ["maize", "beans"],
            "livestock": ["goats"],
            "has_irrigation": False,
            "farming_experience_years": 12,
        },
        "next_of_kin_name": "Jane Tester",
        "next_of_kin_phone": "+260961234567",
    }


# ============================================================
# 🔹 CREATE FARMER
# ============================================================
@pytest.mark.asyncio
async def test_create_farmer(auth_client, sample_farmer_data):
    """✅ Should create a new farmer successfully."""
    response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    assert response.status_code == 201, f"Unexpected: {response.text}"

    data = response.json()
    assert "farmer_id" in data
    assert data["farmer_id"].startswith("ZM")
    assert "created_at" in data
    assert "qr_code_url" in data


@pytest.mark.asyncio
async def test_create_farmer_invalid_nrc(auth_client, sample_farmer_data):
    """🚫 Should reject invalid NRC format."""
    sample_farmer_data["nrc_number"] = "invalid_nrc"
    response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    assert response.status_code == 400
    assert "Invalid NRC number format" in response.text


@pytest.mark.asyncio
async def test_create_farmer_underage(auth_client, sample_farmer_data):
    """🚫 Should reject farmer below minimum age (18)."""
    sample_farmer_data["personal_info"]["date_of_birth"] = "2010-01-01"
    response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    assert response.status_code == 400
    assert "at least 18 years old" in response.text


# ============================================================
# 🔹 FETCH FARMERS
# ============================================================
@pytest.mark.asyncio
async def test_get_farmers_list(auth_client, sample_farmer_data):
    """✅ Should return list of farmers."""
    # Create one farmer
    auth_client.post("/api/farmers/", json=sample_farmer_data)

    response = auth_client.get("/api/farmers/")
    assert response.status_code == 200
    farmers = response.json()
    assert isinstance(farmers, list)
    assert len(farmers) >= 1


@pytest.mark.asyncio
async def test_get_farmer_by_id(auth_client, sample_farmer_data):
    """✅ Should retrieve farmer by farmer_id."""
    create_response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    farmer_id = create_response.json()["farmer_id"]

    response = auth_client.get(f"/api/farmers/{farmer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_id"] == farmer_id
    assert "personal_info" in data
    assert "address" in data


@pytest.mark.asyncio
async def test_get_nonexistent_farmer(auth_client):
    """🚫 Should return 404 for unknown farmer_id."""
    response = auth_client.get("/api/farmers/ZM999999")
    assert response.status_code == 404
    assert "Farmer not found" in response.text


# ============================================================
# 🔹 UPDATE FARMER
# ============================================================
@pytest.mark.asyncio
async def test_update_farmer(auth_client, sample_farmer_data):
    """✅ Should update an existing farmer record."""
    create_response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    farmer_id = create_response.json()["farmer_id"]

    update_payload = {"notes": "Updated test notes"}
    response = auth_client.put(f"/api/farmers/{farmer_id}", json=update_payload)
    assert response.status_code == 200
    updated = response.json()
    assert updated["notes"] == "Updated test notes"


@pytest.mark.asyncio
async def test_update_invalid_farmer(auth_client):
    """🚫 Should fail to update non-existent farmer."""
    update_payload = {"notes": "Invalid farmer test"}
    response = auth_client.put("/api/farmers/ZM999999", json=update_payload)
    assert response.status_code == 404
    assert "Farmer not found" in response.text


# ============================================================
# 🔹 DELETE FARMER
# ============================================================
@pytest.mark.asyncio
async def test_delete_farmer(auth_client, sample_farmer_data):
    """✅ Should delete farmer record."""
    create_response = auth_client.post("/api/farmers/", json=sample_farmer_data)
    farmer_id = create_response.json()["farmer_id"]

    delete_response = auth_client.delete(f"/api/farmers/{farmer_id}")
    assert delete_response.status_code in (200, 204)

    # Verify deletion
    get_response = auth_client.get(f"/api/farmers/{farmer_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_farmer(auth_client):
    """🚫 Should handle deleting missing farmer gracefully."""
    response = auth_client.delete("/api/farmers/ZM000999")
    assert response.status_code == 404
    assert "Farmer not found" in response.text
