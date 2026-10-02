import os
import pytest

# Use a completely separate database for tests.
os.environ["DATABASE_URL"] = (
    "postgresql+psycopg2://postgres:postgres"
    "@localhost:5432/eve_healthcare_test"
)

os.environ["JWT_SECRET"] = "test-secret"

from fastapi.testclient import TestClient

from app.database import Base, engine, SessionLocal
from app.main import app
from app.seed import seed_database

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    seed_database()

    yield

    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def auth_headers(client):
    import uuid

    email = f"testuser_{uuid.uuid4().hex}@example.com"
    password = "Test@12345"

    signup_response = client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": email,
            "password": password,
        },
    )

    assert signup_response.status_code in [200, 201]

    login_response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }