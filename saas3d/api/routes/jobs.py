from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Job, JobStatus, User
from schemas import JobCreate, JobResponse
from routes.auth import get_current_user

router = APIRouter()

def create_job(db: Session, user_id: int, input_key: str, task_id: str = None) -> Job:
    """Crear nuevo job"""
    job = Job(
        user_id=user_id,
        input_key=input_key,
        task_id=task_id,
        status=JobStatus.queued
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def get_job(db: Session, job_id: int, user_id: int) -> Job:
    """Obtener job por ID y usuario"""
    job = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    return job

def get_user_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Job]:
    """Obtener jobs del usuario"""
    return db.query(Job).filter(Job.user_id == user_id).offset(skip).limit(limit).all()

def update_job_status(db: Session, job_id: int, status: JobStatus, progress: int = None, error: str = None, output_key: str = None):
    """Actualizar estado del job"""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        return None
    
    job.status = status
    if progress is not None:
        job.progress = progress
    if error is not None:
        job.error = error
    if output_key is not None:
        job.output_key = output_key
    if status in [JobStatus.completed, JobStatus.failed]:
        job.finished_at = datetime.utcnow()
    
    db.commit()
    db.refresh(job)
    return job

@router.post("/jobs", response_model=JobResponse)
def create_job_endpoint(
    job: JobCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo job"""
    db_job = create_job(db, current_user.id, job.input_key)
    return db_job

@router.get("/jobs", response_model=List[JobResponse])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener jobs del usuario"""
    jobs = get_user_jobs(db, current_user.id, skip, limit)
    return jobs

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_job_endpoint(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtener job específico"""
    job = get_job(db, job_id, current_user.id)
    return job

@router.delete("/jobs/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Eliminar job"""
    job = get_job(db, job_id, current_user.id)
    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}
