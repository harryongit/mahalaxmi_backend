from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

# Many-to-many relationship for Service <-> Festival
service_festival_association = Table(
    'service_festival',
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.id'), primary_key=True),
    Column('festival_id', Integer, ForeignKey('festivals.id'), primary_key=True)
)

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    services = relationship("Service", back_populates="category")

class Festival(Base):
    __tablename__ = "festivals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    
    services = relationship("Service", secondary=service_festival_association, back_populates="festivals")

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)
    
    description = Column(Text, nullable=True)
    short_description = Column(String(255), nullable=True)
    
    price = Column(Integer, nullable=True) # Stored in paise/cents
    is_custom_amount = Column(Boolean, default=False)
    min_amount = Column(Integer, nullable=True)
    
    active_from = Column(Date, nullable=True)
    active_to = Column(Date, nullable=True)
    
    is_active = Column(Boolean, default=True)
    display_order = Column(Integer, default=0)
    icon = Column(String(50), nullable=True)
    inclusions = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    category = relationship("Category", back_populates="services")
    festivals = relationship("Festival", secondary=service_festival_association, back_populates="services")
