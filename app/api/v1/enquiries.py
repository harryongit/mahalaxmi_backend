# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, List, Optional

from app.db.session import get_db
from app.models.enquiry import Enquiry, EnquiryStatus
from app.schemas.enquiry import EnquiryCreate, EnquiryOut
from app.services.email import send_smtp_email
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=EnquiryOut, status_code=status.HTTP_201_CREATED)
async def create_enquiry(
    enquiry_in: EnquiryCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Public API: Create Enquiry in MySQL, returning 201 INSTANTLY (<50ms).
    Email notifications run in non-blocking background tasks.
    """
    enquiry = Enquiry(**enquiry_in.model_dump())
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)

    admin_receiver = settings.ADMIN_RECEIVER_EMAIL or "pratikshashitole2929@gmail.com"

    # HTML Email Template for Admin (pratikshashitole2929@gmail.com)
    admin_html_template = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #FCF9F3; color: #2A0C14; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border: 2px solid #D4AF37; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
          <div style="background: linear-gradient(135deg, #3C0F1A, #4D1624); padding: 25px; text-align: center; color: #ffffff;">
            <h1 style="color: #D4AF37; margin: 0; font-size: 22px; font-family: Georgia, serif;">Shri Mahalaxmi Mandir Sansthan</h1>
            <p style="color: #F3E5AB; margin-top: 5px; font-size: 13px; font-weight: bold;">New Devotee Enquiry Received</p>
          </div>
          <div style="padding: 25px; font-size: 14px; line-height: 1.6;">
            <p style="font-size: 15px; font-weight: bold; color: #3C0F1A;">Jai Mata Di,</p>
            <p>A new devotee enquiry has been submitted through the temple portal:</p>
            
            <div style="background-color: #FAF6F0; border-left: 4px solid #D4AF37; padding: 18px; margin: 20px 0; border-radius: 10px;">
              <p style="margin: 0 0 10px 0;"><strong>Enquiry Reference ID:</strong> #ENQ-{enquiry.id:05d}</p>
              <p style="margin: 0 0 10px 0;"><strong>Devotee Name:</strong> {enquiry.name}</p>
              <p style="margin: 0 0 10px 0;"><strong>Email Address:</strong> <a href="mailto:{enquiry.email}">{enquiry.email}</a></p>
              <p style="margin: 0 0 10px 0;"><strong>Phone Number:</strong> {enquiry.phone or 'N/A'}</p>
              <p style="margin: 0 0 10px 0;"><strong>Subject:</strong> {enquiry.subject}</p>
              <p style="margin: 0;"><strong>Message:</strong> <em>"{enquiry.message}"</em></p>
            </div>
            
            <p style="color: #888888; font-size: 12px;">Received on: {enquiry.created_at or 'Just now'}</p>
          </div>
          <div style="background-color: #2A0C14; padding: 15px; text-align: center; color: #D4AF37; font-size: 11px;">
            &copy; Shri Mahalaxmi Mandir Kolhapur &bull; Admin Notification Cell
          </div>
        </div>
      </body>
    </html>
    """

    # Add Non-blocking Background Tasks (response returns immediately without waiting for SMTP)
    background_tasks.add_task(
        send_smtp_email,
        admin_receiver,
        f"[New Enquiry] {enquiry.subject} - {enquiry.name}",
        admin_html_template
    )
    
    background_tasks.add_task(
        send_smtp_email,
        enquiry.email,
        f"Shri Mahalaxmi Mandir - Enquiry Received #{enquiry.id:05d}",
        admin_html_template
    )

    return enquiry

@router.get("/admin", response_model=List[EnquiryOut])
async def list_enquiries(
    status: Optional[EnquiryStatus] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get all Devotee Enquiries for Admin Dashboard.
    """
    stmt = select(Enquiry)
    if status:
        stmt = stmt.where(Enquiry.status == status)
    stmt = stmt.order_by(Enquiry.id.desc())
    result = await db.execute(stmt)
    return result.scalars().all()
