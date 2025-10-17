"""
Endpoints para procesamiento de nubes de puntos
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import os
from pathlib import Path

from database import get_db
from models import Job, User
from auth import get_current_user
from enums import JobStatus
from celery_worker import process_point_cloud_task

router = APIRouter()

class ProcessingRequest(BaseModel):
    """Modelo para solicitud de procesamiento"""
    algorithm: str = "poisson"  # poisson, ball_pivoting, alpha_shape
    voxel_size: float = 0.01
    nb_neighbors: int = 20
    std_ratio: float = 2.0
    normal_radius: float = 0.1
    normal_max_nn: int = 30
    output_format: str = "ply"
    
    # Parámetros específicos por algoritmo
    poisson_depth: int = 9
    poisson_width: int = 0
    poisson_scale: float = 1.1
    poisson_linear_fit: bool = False
    
    ball_pivoting_radii: Optional[List[float]] = None
    
    alpha_shape_alpha: float = 0.1

class ProcessingResponse(BaseModel):
    """Modelo para respuesta de procesamiento"""
    job_id: int
    status: str
    message: str
    task_id: Optional[str] = None

@router.post("/process/{job_id}", response_model=ProcessingResponse)
def start_processing(
    job_id: int,
    processing_request: ProcessingRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Iniciar procesamiento de una nube de puntos"""
    
    # Verificar que el trabajo existe y pertenece al usuario
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trabajo no encontrado"
        )
    
    if job.status != JobStatus.queued:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El trabajo ya está en estado: {job.status}"
        )
    
    # Verificar que el archivo de entrada existe
    input_file_path = Path("saas3d/api/uploads") / job.input_key
    if not input_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Archivo de entrada no encontrado"
        )
    
    # Validar algoritmo
    valid_algorithms = ["poisson", "ball_pivoting", "alpha_shape"]
    if processing_request.algorithm not in valid_algorithms:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Algoritmo no válido. Opciones: {', '.join(valid_algorithms)}"
        )
    
    # Validar formato de salida
    valid_formats = ["ply", "obj", "stl"]
    if processing_request.output_format not in valid_formats:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato de salida no válido. Opciones: {', '.join(valid_formats)}"
        )
    
    try:
        # Preparar parámetros para la tarea
        task_params = {
            'algorithm': processing_request.algorithm,
            'voxel_size': processing_request.voxel_size,
            'nb_neighbors': processing_request.nb_neighbors,
            'std_ratio': processing_request.std_ratio,
            'normal_radius': processing_request.normal_radius,
            'normal_max_nn': processing_request.normal_max_nn,
            'output_format': processing_request.output_format,
            'poisson_depth': processing_request.poisson_depth,
            'poisson_width': processing_request.poisson_width,
            'poisson_scale': processing_request.poisson_scale,
            'poisson_linear_fit': processing_request.poisson_linear_fit,
            'ball_pivoting_radii': processing_request.ball_pivoting_radii,
            'alpha_shape_alpha': processing_request.alpha_shape_alpha,
        }
        
        # Enviar tarea a Celery
        task = process_point_cloud_task.delay(
            job_id=job_id,
            input_file_path=str(input_file_path),
            algorithm=processing_request.algorithm,
            **task_params
        )
        
        # Actualizar trabajo con el task_id
        job.task_id = task.id
        job.status = JobStatus.queued  # Mantener como queued hasta que Celery lo procese
        db.commit()
        
        return ProcessingResponse(
            job_id=job_id,
            status="queued",
            message="Procesamiento iniciado correctamente",
            task_id=task.id
        )
        
    except Exception as e:
        # Marcar trabajo como fallido
        job.status = JobStatus.failed
        job.error = f"Error al iniciar procesamiento: {str(e)}"
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al iniciar procesamiento: {str(e)}"
        )

@router.get("/algorithms")
def get_available_algorithms():
    """Obtener algoritmos de reconstrucción disponibles"""
    return {
        "algorithms": [
            {
                "name": "poisson",
                "display_name": "Poisson Surface Reconstruction",
                "description": "Algoritmo robusto para superficies suaves",
                "parameters": {
                    "poisson_depth": {"type": "int", "default": 9, "min": 1, "max": 15},
                    "poisson_width": {"type": "int", "default": 0, "min": 0, "max": 10},
                    "poisson_scale": {"type": "float", "default": 1.1, "min": 0.1, "max": 2.0},
                    "poisson_linear_fit": {"type": "bool", "default": False}
                }
            },
            {
                "name": "ball_pivoting",
                "display_name": "Ball Pivoting Algorithm",
                "description": "Algoritmo basado en esferas rodantes",
                "parameters": {
                    "ball_pivoting_radii": {"type": "list", "default": None, "description": "Lista de radios para las esferas"}
                }
            },
            {
                "name": "alpha_shape",
                "display_name": "Alpha Shape",
                "description": "Algoritmo basado en formas alfa",
                "parameters": {
                    "alpha_shape_alpha": {"type": "float", "default": 0.1, "min": 0.01, "max": 1.0}
                }
            }
        ],
        "common_parameters": {
            "voxel_size": {"type": "float", "default": 0.01, "min": 0.001, "max": 0.1},
            "nb_neighbors": {"type": "int", "default": 20, "min": 5, "max": 100},
            "std_ratio": {"type": "float", "default": 2.0, "min": 0.1, "max": 5.0},
            "normal_radius": {"type": "float", "default": 0.1, "min": 0.01, "max": 1.0},
            "normal_max_nn": {"type": "int", "default": 30, "min": 5, "max": 100},
            "output_format": {"type": "str", "options": ["ply", "obj", "stl"], "default": "ply"}
        }
    }

@router.get("/task-status/{task_id}")
def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Obtener estado de una tarea de Celery"""
    try:
        from celery_worker import celery_app
        task_result = celery_app.AsyncResult(task_id)
        
        return {
            "task_id": task_id,
            "status": task_result.status,
            "result": task_result.result if task_result.ready() else None,
            "ready": task_result.ready(),
            "successful": task_result.successful() if task_result.ready() else False,
            "failed": task_result.failed() if task_result.ready() else False
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estado de la tarea: {str(e)}"
        )
