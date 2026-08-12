from pydantic import BaseModel, EmailStr

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminLoginResponse(BaseModel):
    message: str
    admin_id: int

class AdminVerify2FA(BaseModel):
    admin_id: int
    otp: str
