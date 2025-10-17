import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_item():
    return {
        "item_name": "Seed Bags",
        "category": "Agriculture",
        "quantity": 20,
        "unit": "bag",
        "reorder_level": 5,
        "supplier": "ZamAgro",
        "unit_price": 100.0
    }

def test_create_inventory_item(admin_token, sample_item):
    response = client.post("/api/inventory/", json=sample_item, headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code in [200, 201]

def test_low_stock_items(admin_token):
    response = client.get("/api/inventory/low-stock", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert "low_stock_items" in response.json()

def test_transaction_log(admin_token):
    response = client.post(
        "/api/inventory/transactions/",
        params={"item_id": "INV00001", "quantity": 5, "transaction_type": "issue"},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
