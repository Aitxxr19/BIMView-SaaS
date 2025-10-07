from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BIMView API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"])

@app.get("/")
def read_root():
    return {"message": "BIMView API", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
