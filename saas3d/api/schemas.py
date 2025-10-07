from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enums import JobStatus

# Esquemas para requests
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class JobCreate(BaseModel):
    input_key: str

# Esquemas para responses
class UserResponse(BaseModel):
    id: int
    email: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: int
    user_id: int
    input_key: Optional[str]
    output_key: Optional[str]
    status: JobStatus
    progress: int
    error: Optional[str]
    task_id: Optional[str]
    created_at: datetime
    finished_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
