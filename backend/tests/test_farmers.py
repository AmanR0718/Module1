import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_farmer_data():
    """Sample farmer data for testing"""
    return {
        "personal_info": {
            "first_name": "John",
            "last_name": "Test",
            "phone_primary": "+260-97-1234567",
            "date_of_birth": "1985-05-15",
            "gender": "male"
        },
        "address": {
            "province": "Central",
            "district": "Chibombo",
            "village": "Test Village",
            "gps_coordinates": {
                "latitude": -14.7167,
                "longitude": 28.4333
            }
        },
        "nrc_number": "123456/12/1",
        "land_parcels": [],
        "current_crops": []
    }

def test_create_farmer(admin_token, sample_farmer_data):
    """Test farmer creation"""
    response = client.post(
        "/api/farmers/",
        json=sample_farmer_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "farmer_id" in data
    assert data["farmer_id"].startswith("ZM")
    assert "qr_code" in data

def test_get_farmers(admin_token):
    """Test getting farmers list"""
    response = client.get(
        "/api/farmers/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_farmer_by_id(admin_token, sample_farmer_data):
    """Test getting farmer by ID"""
    # Create farmer first
    create_response = client.post(
        "/api/farmers/",
        json=sample_farmer_data,
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    farmer_id = create_response.json()["farmer_id"]
    
    # Get farmer
    response = client.get(
        f"/api/farmers/{farmer_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["farmer_id"] == farmer_id