import pytest
from httpx import AsyncClient
from app.core import redis as redis_module

VALID_PHONE = "+919876543210"

@pytest.mark.asyncio
async def test_request_otp(client: AsyncClient):
    response = await client.post("/api/v1/auth/otp/request", json={"phone_number": VALID_PHONE})
    assert response.status_code == 200
    assert response.json()["message"] == "OTP sent successfully."

@pytest.mark.asyncio
async def test_request_otp_invalid_phone(client: AsyncClient):
    response = await client.post("/api/v1/auth/otp/request", json={"phone_number": ""})
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_verify_otp_invalid(client: AsyncClient):
    response = await client.post("/api/v1/auth/otp/verify", json={"phone_number": VALID_PHONE, "otp": "000000"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired OTP."

@pytest.mark.asyncio
async def test_verify_otp_valid_and_reuse(client: AsyncClient):
    # 1. Request OTP
    await client.post("/api/v1/auth/otp/request", json={"phone_number": "+919876543211"})

    # Extract from redis (mock)
    key = "otp:+919876543211"
    otp = await redis_module.redis_client.get(key)
    assert otp is not None

    # 2. Verify OTP
    response = await client.post("/api/v1/auth/otp/verify", json={"phone_number": "+919876543211", "otp": otp})
    assert response.status_code == 200
    assert "access_token" in response.json()

    # 3. Try reusing OTP (should fail)
    response_reuse = await client.post("/api/v1/auth/otp/verify", json={"phone_number": "+919876543211", "otp": otp})
    assert response_reuse.status_code == 400