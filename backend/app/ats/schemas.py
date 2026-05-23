from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    department: str = Field(default="")
    description: str = Field(default="")
    requirements: str = Field(default="")
    keywords: str = Field(default="")
    status: str = Field(default="open")


class JobUpdate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[str] = None
    keywords: Optional[str] = None
    status: Optional[str] = None


class JobResponse(BaseModel):
    id: int
    title: str
    department: str
    description: str
    requirements: str
    keywords: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    cv_text: str
    cv_filename: str
    score: float
    status: str
    skills: str
    experience_years: float
    job_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CandidateUpdate(BaseModel):
    status: Optional[str] = None
    score: Optional[float] = None
    job_id: Optional[int] = None


class CvUploadResult(BaseModel):
    candidate: CandidateResponse
    score_result: dict


class InterviewCreate(BaseModel):
    candidate_id: int
    job_id: int
    scheduled_time: str
    duration_minutes: int = Field(default=60, ge=15, le=240)
    notes: str = Field(default="")


class InterviewUpdate(BaseModel):
    status: Optional[str] = None
    scheduled_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    job_id: int
    scheduled_time: datetime
    duration_minutes: int
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InterviewWithDetails(InterviewResponse):
    candidate_name: str = ""
    job_title: str = ""
