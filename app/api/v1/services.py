from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Any, List, Optional

from app.db.session import get_db
from app.models.service import Service, Category, Festival
from app.schemas.service import ServiceOut, ServiceCreate, ServiceUpdate, CategoryOut
from app.api.deps import get_current_active_admin

router = APIRouter()

@router.get("/", response_model=List[ServiceOut])
async def list_services(
    category_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Service).options(selectinload(Service.category), selectinload(Service.festivals))
    if category_id:
        stmt = stmt.where(Service.category_id == category_id)
    if is_active is not None:
        stmt = stmt.where(Service.is_active == is_active)
    
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=ServiceOut)
async def get_service(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Service).options(selectinload(Service.category), selectinload(Service.festivals)).where(Service.id == id)
    result = await db.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    return service

@router.post("/", response_model=ServiceOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_active_admin)])
async def create_service(
    service_in: ServiceCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    data = service_in.model_dump(exclude={"festival_ids"})
    service = Service(**data)
    
    if service_in.festival_ids:
        fest_result = await db.execute(select(Festival).where(Festival.id.in_(service_in.festival_ids)))
        service.festivals = fest_result.scalars().all()
        
    db.add(service)
    await db.commit()
    await db.refresh(service)
    
    # Reload with relationships
    stmt = select(Service).options(selectinload(Service.category), selectinload(Service.festivals)).where(Service.id == service.id)
    res = await db.execute(stmt)
    return res.scalars().first()

@router.put("/{id}", response_model=ServiceOut, dependencies=[Depends(get_current_active_admin)])
async def update_service(
    id: int,
    service_in: ServiceUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Service).options(selectinload(Service.category), selectinload(Service.festivals)).where(Service.id == id)
    result = await db.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    update_data = service_in.model_dump(exclude_unset=True)
    festival_ids = update_data.pop("festival_ids", None)
    for field, value in update_data.items():
        setattr(service, field, value)

    if festival_ids is not None:
        fest_result = await db.execute(select(Festival).where(Festival.id.in_(festival_ids)))
        service.festivals = fest_result.scalars().all()

    db.add(service)
    await db.commit()
    await db.refresh(service)

    stmt = select(Service).options(selectinload(Service.category), selectinload(Service.festivals)).where(Service.id == service.id)
    res = await db.execute(stmt)
    return res.scalars().first()

@router.delete("/{id}", dependencies=[Depends(get_current_active_admin)])
async def delete_service(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    stmt = select(Service).where(Service.id == id)
    result = await db.execute(stmt)
    service = result.scalars().first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    await db.delete(service)
    await db.commit()
    return {"message": "Service deleted successfully"}

@router.get("/categories/", response_model=List[CategoryOut])
async def list_categories(
    db: AsyncSession = Depends(get_db)
) -> Any:
    result = await db.execute(select(Category))
    return result.scalars().all()
