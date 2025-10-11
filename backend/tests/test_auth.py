import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_success():
    """Test successful login"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@zambian-farmers.zm",
            "password": "admin123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_current_user(admin_token):
    """Test getting current user info"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@zambian-farmers.zm"
    assert data["role"] == "admin"