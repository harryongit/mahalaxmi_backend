from pydantic import BaseModel, field_validator
from typing import Optional
import phonenumbers

class OTPRequest(BaseModel):
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number")

class OTPVerify(BaseModel):
    phone_number: str
    otp: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        try:
            parsed = phonenumbers.parse(value, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError("Invalid phone number")

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 6:
            raise ValueError("OTP must be a 6-digit number")
        return value

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int] = None
    is_admin: bool = False