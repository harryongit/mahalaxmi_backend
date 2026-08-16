import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "MahalaxmiPuja.com"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # MySQL Database
    DATABASE_URL: str = "mysql+aiomysql://root:root@localhost:3306/mahalaxmi"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    JWT_SECRET: str = "your-super-secret-jwt-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here!"

    # Razorpay
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    RAZORPAY_WEBHOOK_SECRET: str = ""

    # Twilio
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_NUMBER: str = ""

    # CORS
    BACKEND_CORS_ORIGINS: str = "*"

    # SMTP Configuration
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: Optional[int] = 587
    SMTP_USERNAME: Optional[str] = "pole2929@gmail.com"
    SMTP_USER: Optional[str] = "pole2929@gmail.com"
    SMTP_PASSWORD: Optional[str] = "ywdh qmwf tjuc mynk"
    EMAILS_FROM_EMAIL: Optional[str] = "pole2929@gmail.com"
    EMAILS_FROM_NAME: Optional[str] = "Shri Mahalaxmi Mandir Kolhapur"
    ADMIN_RECEIVER_EMAIL: Optional[str] = "pratikshashitole2929@gmail.com"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
