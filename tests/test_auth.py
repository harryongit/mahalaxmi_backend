import pytest
from httpx import AsyncClient
from app.core.redis import redis_client

@pytest.mark.asyncio
async def test_request_otp(client: AsyncClient):
    response = await client.post("/api/v1/auth/request-otp", json={"phone_number": "+919876543210"})
    assert response.status_code == 200
    assert "OTP requested successfully" in response.json()["message"]

@pytest.mark.asyncio
async def test_verify_otp_invalid(client: AsyncClient):
    response = await client.post("/api/v1/auth/verify-otp", json={"phone_number": "+919876543210", "otp": "000000"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired OTP."

@pytest.mark.asyncio
async def test_verify_otp_valid_and_reuse(client: AsyncClient):
    # 1. Request OTP
    await client.post("/api/v1/auth/request-otp", json={"phone_number": "+919876543211"})
    
    # Extract from redis (mock)
    key = "otp:+919876543211"
    otp = await redis_client.get(key)
    assert otp is not None
    
    # 2. Verify OTP
    response = await client.post("/api/v1/auth/verify-otp", json={"phone_number": "+919876543211", "otp": otp})
    assert response.status_code == 200
    assert "access_token" in response.json()
    
    # 3. Try reusing OTP (should fail)
    response_reuse = await client.post("/api/v1/auth/verify-otp", json={"phone_number": "+919876543211", "otp": otp})
    assert response_reuse.status_code == 400
