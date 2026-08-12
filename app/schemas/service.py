from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date

class FestivalBase(BaseModel):
    name: str

class FestivalOut(FestivalBase):
    id: int
    class Config:
        from_attributes = True

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int
    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    name: str
    slug: str
    category_id: int
    description: Optional[str] = None
    short_description: Optional[str] = None
    price: Optional[int] = None
    is_custom_amount: bool = False
    min_amount: Optional[int] = None
    active_from: Optional[date] = None
    active_to: Optional[date] = None
    is_active: bool = True
    display_order: int = 0
    icon: Optional[str] = None
    inclusions: Optional[str] = None

class ServiceCreate(ServiceBase):
    festival_ids: Optional[List[int]] = []

class ServiceUpdate(ServiceBase):
    name: Optional[str] = None
    slug: Optional[str] = None
    category_id: Optional[int] = None
    festival_ids: Optional[List[int]] = None

class ServiceOut(ServiceBase):
    id: int
    created_at: datetime
    category: CategoryOut
    festivals: List[FestivalOut] = []

    class Config:
        from_attributes = True
