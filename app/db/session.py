import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.db.base import Base

# Import all models so metadata registers all MySQL tables
from app.models.user import User
from app.models.enquiry import Enquiry
from app.models.service import Service
from app.models.order import Order
from app.models.payment import Payment

logger = logging.getLogger(__name__)

# Primary MySQL Database Connection
engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

_tables_created = False

async def get_db():
    global _tables_created
    if not _tables_created:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            _tables_created = True
        except Exception as e:
            logger.warning("Could not auto-create MySQL tables: %s", e)

    async with AsyncSessionLocal() as session:
        yield session
