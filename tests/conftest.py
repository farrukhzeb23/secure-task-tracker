"""
Pytest configuration and shared fixtures for the secure task tracker test suite.

This file serves as the central configuration module for pytest testing framework.
It contains:
- Shared test fixtures that can be used across multiple test modules
- Pytest configuration settings and options
- Common setup and teardown logic for tests
- Database connections, mock objects, and other reusable test components

The conftest.py file is automatically discovered by pytest and makes fixtures
available to all test files in the same directory and subdirectories without
requiring explicit imports.
"""
import pytest
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base, get_db
from app.main import app

# Use SQLite in-memory database for testing
"""
Benefits of SQLite for testing:

Faster test execution
No external dependencies
Isolated tests (fresh database for each test)
No need for PostgreSQL setup in CI/CD
"""
test_url = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(test_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
    bind=test_engine,
)


@pytest.fixture(scope="function")
async def db():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        yield db
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture(scope="function")
async def client(db):
    async def override_get_db():
        yield db
    app.dependency_overrides[get_db] = override_get_db

    async with httpx.AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app)
    ) as ac:
        yield ac
