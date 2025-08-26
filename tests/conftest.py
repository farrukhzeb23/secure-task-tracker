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
from sqlalchemy import text
from app.core.database import Base, get_db
from app.main import app
from datetime import timedelta, datetime, timezone
from app.core.security import create_access_token, create_refresh_token, hash_refresh_token
from app.core.config import settings
from app.models.refresh_token import RefreshToken

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
        # Insert default roles without hyphens to match SQLAlchemy UUID format
        await connection.execute(text("""
            INSERT INTO roles (id, name, description) VALUES 
            ('2f14539c89f54222b51869392c45c6fd', 'admin', 'Administrator with full access'),
            ('42bc5587b83f4232bf531b3ab60902f2', 'user', 'Regular user with limited access')
        """))
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


@pytest.fixture
async def test_user(db):
    from app.models.user import User
    from app.core.security import hash_password
    from app.services.role_service import assign_roles_to_user, get_user_with_roles
    user = User(
        email="testuser@example.com",
        username="test.user",
        full_name="test user",
        password=hash_password("testpass")
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await assign_roles_to_user(str(user.id), ["user"], db)
    await db.commit()
    # Get user with roles to ensure the relationship is properly loaded
    user_with_roles = await get_user_with_roles(str(user.id), db)
    return user_with_roles


@pytest.fixture
async def test_admin_user(db):
    from app.models.user import User
    from app.core.security import hash_password
    from app.services.role_service import assign_roles_to_user, get_user_with_roles
    user = User(
        email="admin@example.com",
        username="admin.user",
        full_name="admin user",
        password=hash_password("testpass")
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    await assign_roles_to_user(str(user.id), ["admin"], db)
    await db.commit()
    # Get user with roles to ensure the relationship is properly loaded
    user_with_roles = await get_user_with_roles(str(user.id), db)
    return user_with_roles


@pytest.fixture
async def test_refresh_token(db, test_user):
    refresh_token = create_refresh_token()
    expires_at = datetime.now(timezone.utc) + \
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_refresh_token = RefreshToken(
        user_id=test_user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    await db.commit()
    return refresh_token


@pytest.fixture
def test_access_token(test_user):
    return create_access_token(data={"sub": str(test_user.id)})


@pytest.fixture
def test_admin_access_token(test_admin_user):
    return create_access_token(data={"sub": str(test_admin_user.id)})
