import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from app.main import app

client = TestClient(app)

def test_sync_batch(admin_token):
    sample_data = {
        "farmers": [{
            "personal_info": {"first_name": "Aman", "last_name": "Sync", "phone_primary": "+260971234567"},
            "address": {"province": "Central", "district": "Chibombo", "village": "Sync Village"},
            "nrc_number": "123456/12/1"
        }],
        "last_sync": datetime.utcnow().isoformat()
    }

    response = client.post("/api/sync/batch", json=sample_data, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code in [200, 201]
    data = response.json()
    assert "successful" in data

def test_sync_status(admin_token):
    response = client.get(
        f"/api/sync/status?last_sync={datetime.utcnow().isoformat()}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "updates_count" in response.json()
