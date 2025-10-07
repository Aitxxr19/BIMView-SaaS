import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_register_user(setup_database):
    """Test registro de usuario"""
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_register_duplicate_email(setup_database):
    """Test registro con email duplicado"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    
    # Intentar registrar el mismo email
    response = client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(setup_database):
    """Test login exitoso"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "testpassword"
    })
    
    # Hacer login
    response = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(setup_database):
    """Test login con contraseña incorrecta"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "wrongpass@example.com",
        "password": "testpassword"
    })
    
    # Intentar login con contraseña incorrecta
    response = client.post("/auth/login", json={
        "email": "wrongpass@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_current_user(setup_database):
    """Test obtener usuario actual"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "current@example.com",
        "password": "testpassword"
    })
    
    # Hacer login
    login_response = client.post("/auth/login", json={
        "email": "current@example.com",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Obtener usuario actual
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "current@example.com"
