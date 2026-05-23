from pydantic import BaseModel, Field
from typing import Optional, List


class AttendanceCreate(BaseModel):
    employee_id: str
    date: Optional[str] = ""
    check_in: Optional[str] = ""
    check_out: Optional[str] = ""
    hours_worked: Optional[float] = 0.0


class AttendanceResponse(BaseModel):
    employee_id: str
    date: str
    check_in: str
    check_out: str
    hours_worked: float

    class Config:
        from_attributes = True
