from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.enquiry import EnquiryStatus

class EnquiryCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: str
    message: str

class EnquiryRespond(BaseModel):
    admin_reply: str

class EnquiryStatusUpdate(BaseModel):
    status: EnquiryStatus

class EnquiryOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    subject: str
    message: str
    status: EnquiryStatus
    admin_reply: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
