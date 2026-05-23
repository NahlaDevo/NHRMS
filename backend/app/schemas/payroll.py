from pydantic import BaseModel, Field
from typing import Optional, List


class PayrollGenerate(BaseModel):
    base_salary: float = 10000

    class Config:
        from_attributes = True


class PayrollResponse(BaseModel):
    employee_id: str
    month: str
    base_salary: float
    total_hours: float
    overtime: float
    deductions: float
    net_salary: float

    class Config:
        from_attributes = True
