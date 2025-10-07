import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database import get_db, Base
from models import JobStatus

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
def auth_headers(setup_database):
    """Crear usuario y obtener token de autenticación"""
    # Registrar usuario
    client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    
    # Hacer login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

def test_create_job(auth_headers):
    """Test crear job"""
    response = client.post("/api/jobs", json={
        "input_key": "test-input.ply"
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["input_key"] == "test-input.ply"
    assert data["status"] == JobStatus.queued
    assert data["progress"] == 0
    assert "id" in data

def test_get_jobs(auth_headers):
    """Test obtener jobs del usuario"""
    # Crear un job
    client.post("/api/jobs", json={
        "input_key": "test-input2.ply"
    }, headers=auth_headers)
    
    # Obtener jobs
    response = client.get("/api/jobs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(job["user_id"] for job in data)

def test_get_job_by_id(auth_headers):
    """Test obtener job específico"""
    # Crear job
    create_response = client.post("/api/jobs", json={
        "input_key": "test-input3.ply"
    }, headers=auth_headers)
    job_id = create_response.json()["id"]
    
    # Obtener job específico
    response = client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == job_id
    assert data["input_key"] == "test-input3.ply"

def test_get_job_not_found(auth_headers):
    """Test obtener job que no existe"""
    response = client.get("/api/jobs/99999", headers=auth_headers)
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]

def test_delete_job(auth_headers):
    """Test eliminar job"""
    # Crear job
    create_response = client.post("/api/jobs", json={
        "input_key": "test-input4.ply"
    }, headers=auth_headers)
    job_id = create_response.json()["id"]
    
    # Eliminar job
    response = client.delete(f"/api/jobs/{job_id}", headers=auth_headers)
    assert response.status_code == 200
    assert "Job deleted successfully" in response.json()["message"]
    
    # Verificar que el job fue eliminado
    get_response = client.get(f"/api/jobs/{job_id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_jobs_require_authentication():
    """Test que los endpoints de jobs requieren autenticación"""
    response = client.post("/api/jobs", json={
        "input_key": "test-input.ply"
    })
    assert response.status_code == 401
    
    response = client.get("/api/jobs")
    assert response.status_code == 401
