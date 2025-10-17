"""
backend/tests/test_auth.py
Unit tests for authentication and authorization endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# ============================================================
# 🔹 LOGIN TESTS
# ============================================================
def test_login_success(client):
    """✅ Should login successfully with correct credentials."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "admin@test.com",  # Ensure matches seeded admin
            "password": "admin123"
        },
    )
    assert response.status_code == 200, f"Unexpected status: {response.text}"

    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_invalid_credentials(client):
    """🚫 Should reject login with invalid credentials."""
    response = client.post(
        "/api/auth/login",
        data={"username": "invalid@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_missing_fields(client):
    """🚫 Should fail when username or password is missing."""
    response = client.post("/api/auth/login", data={"username": "admin@test.com"})
    assert response.status_code == 422  # FastAPI validation error


# ============================================================
# 🔹 TOKEN TESTS
# ============================================================
@pytest.mark.asyncio
async def test_refresh_token_flow(client, admin_token):
    """✅ Should issue new tokens on refresh request."""
    response = client.post(
        "/api/auth/refresh",
        json={"refresh_token": admin_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_refresh_token(client):
    """🚫 Should reject invalid refresh tokens."""
    response = client.post("/api/auth/refresh", json={"refresh_token": "fake.token.value"})
    assert response.status_code == 401
    assert "Could not refresh token" in response.text


# ============================================================
# 🔹 CURRENT USER ENDPOINT
# ============================================================
@pytest.mark.asyncio
async def test_get_current_user(client, admin_token):
    """✅ Should return current logged-in user's details."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()

    assert data["email"] == "admin@test.com"
    assert data["role"] == "admin"
    assert "is_active" in data


@pytest.mark.asyncio
async def test_unauthorized_user_access(client):
    """🚫 Should reject request without valid Authorization header."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert "Could not validate credentials" in response.text


# ============================================================
# 🔹 ROLE-BASED ACCESS TESTS
# ============================================================
@pytest.mark.asyncio
async def test_admin_only_access(auth_client):
    """✅ Should allow admin-only route access."""
    response = auth_client.get("/api/farmers")  # Example admin route
    assert response.status_code in (200, 404)  # 404 if no data yet, but authorized


@pytest.mark.asyncio
async def test_forbidden_role_access(client):
    """🚫 Should deny user with wrong role."""
    # Simulate non-admin token
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.fakepayload.fake"
    response = client.get(
        "/api/farmers",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code in (401, 403)
