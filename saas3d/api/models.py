from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from enums import JobStatus

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relación con Jobs
    jobs = relationship("Job", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class Job(Base):
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    input_key = Column(String, index=True)  # Clave del archivo de entrada en S3
    output_key = Column(String, index=True)  # Clave del archivo de salida en S3
    status = Column(Enum(JobStatus), default=JobStatus.queued)
    progress = Column(Integer, default=0)  # Progreso de 0 a 100
    error = Column(Text)  # Mensaje de error si falla
    task_id = Column(String, index=True)  # ID de la tarea Celery
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    
    # Relación con User
    user = relationship("User", back_populates="jobs")
    
    def __repr__(self):
        return f"<Job(id={self.id}, user_id={self.user_id}, status='{self.status}')>"
