import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from io import BytesIO

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

@pytest.fixture(scope="module")
def auth_token(setup_database):
    """Crear usuario y obtener token de autenticación"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "upload@example.com",
        "password": "testpassword"
    })
    
    # Hacer login
    response = client.post("/auth/login", json={
        "email": "upload@example.com",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    
    return token

def test_upload_file_success(auth_token):
    """Test subida de archivo exitosa"""
    # Crear archivo de prueba
    file_content = b"test point cloud data"
    file = BytesIO(file_content)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {"file": ("test.ply", file, "application/octet-stream")}
    
    response = client.post("/api/upload", headers=headers, files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "filename" in data
    assert "job_id" in data

def test_upload_file_no_auth():
    """Test subida de archivo sin autenticación"""
    file_content = b"test point cloud data"
    file = BytesIO(file_content)
    
    files = {"file": ("test.ply", file, "application/octet-stream")}
    
    response = client.post("/api/upload", files=files)
    assert response.status_code == 401

def test_upload_file_wrong_extension(auth_token):
    """Test subida de archivo con extensión incorrecta"""
    file_content = b"test data"
    file = BytesIO(file_content)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {"file": ("test.txt", file, "text/plain")}
    
    response = client.post("/api/upload", headers=headers, files=files)
    assert response.status_code == 400
    assert "no permitido" in response.json()["detail"].lower()

def test_upload_file_too_large(auth_token):
    """Test subida de archivo demasiado grande"""
    # Crear archivo de más de 100MB
    file_content = b"x" * (101 * 1024 * 1024)  # 101MB
    file = BytesIO(file_content)
    
    headers = {"Authorization": f"Bearer {auth_token}"}
    files = {"file": ("large.ply", file, "application/octet-stream")}
    
    response = client.post("/api/upload", headers=headers, files=files)
    assert response.status_code == 413
