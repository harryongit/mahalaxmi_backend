import pytest
import pytest_asyncio
import fakeredis.aioredis
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core import redis as redis_module

collect_ignore = ["load_test.py"]

# Use an in-memory SQLite database for testing, or a test Postgres DB
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def redis_override():
    fake = fakeredis.aioredis.FakeRedis(decode_responses=True)
    original = redis_module.redis_client
    redis_module.redis_client = fake
    from app.services import auth as auth_service
    auth_service.redis_client = fake
    yield
    redis_module.redis_client = original
    auth_service.redis_client = original

@pytest_asyncio.fixture(autouse=True)
async def db_setup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
