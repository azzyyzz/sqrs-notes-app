import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.models import Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

# Create tables
Base.metadata.create_all(bind=engine)


# Dependency override
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


# Test client fixture
@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


# Test data
@pytest.fixture
def test_user_data():
    return {"username": "testuser", "password": "testpass"}


@pytest.fixture
def test_note_data():
    return {"title": "Test Note", "content": "Test Content"}


# Test user fixture
@pytest.fixture
def test_user(client, test_user_data):
    response = client.post("/users/", json=test_user_data)
    assert response.status_code == 200
    return response.json()


# Auth token fixture
@pytest.fixture
def auth_token(client, test_user, test_user_data):
    response = client.post(
        "/token",
        data={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


# Auth headers fixture
@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# Test note fixture
@pytest.fixture
def test_note(client, auth_headers, test_note_data):
    response = client.post(
        "/notes/", json=test_note_data, headers=auth_headers
    )
    assert response.status_code == 200
    return response.json()


# Clean up database after tests
@pytest.fixture(autouse=True)
def cleanup_db():
    yield
    # Clear all data after each test
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_login_for_access_token(client, test_user, test_user_data):
    # Test successful login
    response = client.post(
        "/token",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"],
        },  # Changed data= to json=
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test login with invalid credentials
    response = client.post(
        "/token",
        json={
            "username": test_user_data["username"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]

    # Test login with non-existent user
    response = client.post(
        "/token", json={"username": "nonexistent", "password": "password"}
    )
    assert response.status_code == 401


def test_create_user(client):
    # Test successful user creation
    user_data = {"username": "newuser", "password": "newpass"}
    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user_data["username"]
    assert "id" in data

    # Test duplicate user creation
    response = client.post("/users/", json=user_data)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]


def test_unauthenticated_access_to_protected_routes(client):
    # Test accessing protected routes without authentication
    protected_routes = [
        ("POST", "/notes/", {}),
        ("GET", "/notes/", None),
        ("PUT", "/notes/1", {}),
        ("DELETE", "/notes/1", None),
        ("POST", "/translate/", {"text": "hello"}),
        ("GET", "/users/me", None),
    ]

    for method, route, payload in protected_routes:
        if method == "POST":
            response = client.post(route, json=payload)
        elif method == "GET":
            response = client.get(route)
        elif method == "PUT":
            response = client.put(route, json=payload)
        elif method == "DELETE":
            response = client.delete(route)

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
