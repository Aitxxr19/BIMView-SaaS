from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path

from database import get_db
from models import User
from auth import get_current_user

router = APIRouter()

# Configuración de archivos
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".ply", ".las", ".laz", ".pcd", ".xyz"}
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

def validate_file(file: UploadFile) -> bool:
    """Validar archivo de entrada"""
    if not file.filename:
        return False
    
    # Verificar extensión
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False
    
    return True

def generate_unique_filename(original_filename: str) -> str:
    """Generar nombre único para el archivo"""
    file_ext = Path(original_filename).suffix
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_ext}"

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Subir archivo de nube de puntos"""
    
    # Validar archivo
    if not validate_file(file):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Verificar tamaño del archivo
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande. Tamaño máximo: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generar nombre único
    unique_filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / unique_filename
    
    # Guardar archivo
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Crear entrada en la base de datos (Job)
        from models import Job, JobStatus
        job = Job(
            user_id=current_user.id,
            input_key=unique_filename,
            status=JobStatus.queued
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        return {
            "message": "Archivo subido exitosamente",
            "filename": file.filename,
            "unique_filename": unique_filename,
            "job_id": job.id,
            "file_size": len(file_content),
            "file_path": str(file_path)
        }
        
    except Exception as e:
        # Limpiar archivo si hay error
        if file_path.exists():
            file_path.unlink()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al guardar archivo: {str(e)}"
        )

@router.get("/files/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Descargar archivo"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    # Verificar que el usuario tiene acceso al archivo
    # (implementar lógica de verificación si es necesario)
    
    from fastapi.responses import FileResponse
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type='application/octet-stream'
    )

@router.delete("/files/{filename}")
async def delete_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """Eliminar archivo"""
    file_path = UPLOAD_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo no encontrado"
        )
    
    try:
        file_path.unlink()
        return {"message": "Archivo eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar archivo: {str(e)}"
        )
