"""
Modelos de prueba para tests
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from test_config import Base
import enum

class JobStatus(str, enum.Enum):
    queued = 'queued'
    processing = 'processing'
    completed = 'completed'
    failed = 'failed'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    jobs = relationship("Job", back_populates="user")

class Job(Base):
    __tablename__ = 'jobs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    input_key = Column(String, index=True)
    output_key = Column(String, index=True)
    status = Column(Enum(JobStatus), default=JobStatus.queued)
    progress = Column(Integer, default=0)
    error = Column(Text)
    task_id = Column(String, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
    user = relationship("User", back_populates="jobs")
