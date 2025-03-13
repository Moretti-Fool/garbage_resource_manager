
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

# Use asyncpg driver
DATABASE_URL = settings.DATABASE_URL



engine = create_async_engine(DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=engine
)


Base = declarative_base()
# Async dependency for FastAPI
async def get_db():
    async with SessionLocal() as session:
        yield session
