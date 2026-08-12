import enum
import hashlib
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, Text
from sqlalchemy.sql import func
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import FernetEngine
from app.db.base import Base
from app.core.config import settings

def get_hash(value: str) -> str:
    if not value:
        return None
    # Use SHA-256 for hashing searchable fields
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

class GanEnum(str, enum.Enum):
    RAKSHASA = "Rakshasa"
    MANUSHYA = "Manushya"
    DEVA = "Deva"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Hashed fields for exact lookup (indexes)
    phone_number_hash = Column(String(64), unique=True, index=True, nullable=False)
    email_hash = Column(String(64), unique=True, index=True, nullable=True)
    
    # Password for admin users
    hashed_password = Column(String(255), nullable=True)
    
    # Encrypted fields for data at rest
    phone_number = Column(EncryptedType(String(20), settings.ENCRYPTION_KEY, FernetEngine), nullable=False)

    first_name = Column(EncryptedType(String(50), settings.ENCRYPTION_KEY, FernetEngine), nullable=True)
    last_name = Column(EncryptedType(String(50), settings.ENCRYPTION_KEY, FernetEngine), nullable=True)
    email = Column(EncryptedType(String(100), settings.ENCRYPTION_KEY, FernetEngine), nullable=True)
    
    gotra = Column(String(50), nullable=True)
    gan = Column(Enum(GanEnum), nullable=True)
    
    address = Column(EncryptedType(Text, settings.ENCRYPTION_KEY, FernetEngine), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(50), nullable=True)
    pin_code = Column(String(20), nullable=True)
    country = Column(String(50), nullable=True)
    
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    whatsapp_opt_in = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
