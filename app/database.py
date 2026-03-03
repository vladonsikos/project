from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Async engine for FastAPI
engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True,
)

# Base class for models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session"""
    async with async_session_maker() as session:
        yield session


async def init_db():
    """Create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
