from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

async_engine = create_async_engine(url)
AysncSessionLocal = async_sessionmaker(
    autoflush=False, bind=async_engine, autocommit=False, class_=AsyncSession
)

Base = declarative_base()


"""
What yield does:
Pauses execution at the yield statement and returns the database session (db) to the caller
Waits for the caller to finish using the database session
Resumes execution after yield when the caller is done, running the finally block to clean up
"""


async def get_db():
    async with AysncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
