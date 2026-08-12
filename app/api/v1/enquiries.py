from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Any, List

from app.db.session import get_db
from app.models.enquiry import Enquiry, EnquiryStatus
from app.schemas.enquiry import EnquiryCreate, EnquiryOut, EnquiryRespond, EnquiryStatusUpdate
from app.api.deps import get_current_active_admin

router = APIRouter()

@router.post("/", response_model=EnquiryOut, status_code=status.HTTP_201_CREATED)
async def create_enquiry(
    enquiry_in: EnquiryCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    enquiry = Enquiry(**enquiry_in.model_dump())
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)
    return enquiry

@router.get("/admin", response_model=List[EnquiryOut], dependencies=[Depends(get_current_active_admin)])
async def list_enquiries(
    status: EnquiryStatus = EnquiryStatus.OPEN,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Enquiry)
    if status:
        stmt = stmt.where(Enquiry.status == status)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.patch("/admin/{id}/respond", response_model=EnquiryOut, dependencies=[Depends(get_current_active_admin)])
async def respond_to_enquiry(
    id: int,
    respond_in: EnquiryRespond,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Enquiry).where(Enquiry.id == id)
    result = await db.execute(stmt)
    enquiry = result.scalars().first()
    
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
        
    enquiry.admin_reply = respond_in.admin_reply
    enquiry.status = EnquiryStatus.RESOLVED
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)
    
    from app.worker.tasks import send_email_notification, dispatch
    dispatch(send_email_notification, enquiry.email, f"Re: {enquiry.subject}", f"Dear {enquiry.name},\n\n{respond_in.admin_reply}")
    
    return enquiry

@router.patch("/admin/{id}/status", response_model=EnquiryOut, dependencies=[Depends(get_current_active_admin)])
async def update_enquiry_status(
    id: int,
    status_in: EnquiryStatusUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Enquiry).where(Enquiry.id == id)
    result = await db.execute(stmt)
    enquiry = result.scalars().first()
    
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
        
    enquiry.status = status_in.status
    db.add(enquiry)
    await db.commit()
    await db.refresh(enquiry)
    return enquiry
