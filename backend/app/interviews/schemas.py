from pydantic import BaseModel, Field
from typing import Optional


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
