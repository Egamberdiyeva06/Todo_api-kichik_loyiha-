import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from dotenv import load_dotenv
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app

load_dotenv()

DATABASE_URL = os.getenv("TEST_DATABASE_URL") or "sqlite+aiosqlite:///./test.db"


test_engine = create_async_engine(DATABASE_URL,
                       connect_args={'check_same_thread': False}
                    )

TestSession = async_sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)

async def override_get_db():
    async with TestSession() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_create_user(ac: AsyncClient):
    response = await ac.post("/api/users/", json={
        "username": "tester",
         "first_name": "Test",
         "last_name": "Loyiha",
         "password": "strongpassword"
         })
    
    assert response.status_code == 200
    assert response.json()["username"] == "tester"


@pytest.mark.asyncio
async def test_create_todo_authenticated(ac: AsyncClient):
    login_res = await ac.post("/api/users/login", data={
        "username": "tester",
        "password": "strongpassword"
    })
    token = login_res.json()["access_token"]
    
    todo_res = await ac.post("/api/todos/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Yangi vazifa",
            "description": "Test tavsifi",
            "priority": "high"
        }
    )
    
    assert todo_res.status_code == 200
    assert todo_res.json()["name"] == "Yangi vazifa"


@pytest.mark.asyncio
async def test_get_users_list(ac: AsyncClient):
    """Foydalanuvchilar ro'yxatini olish (Relationship'larni tekshirish)"""
    response = await ac.get("/api/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)