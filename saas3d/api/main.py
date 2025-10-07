from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes.auth import router as auth_router
from routes.jobs import router as jobs_router

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="BIMView API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])

# Incluir routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])
app.include_router(jobs_router, prefix="/api", tags=["jobs"])

@app.get("/")
def read_root():
    return {"message": "BIMView API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
