from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import date, datetime


class EmployeeCreate(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=200)
    department: str = Field(..., min_length=1, max_length=100)
    position: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., max_length=200)
    phone_number: str = Field(..., max_length=20)
    address: Optional[str] = Field(default="", max_length=500)
    national_id: Optional[str] = Field(default="", max_length=50)
    date_of_birth: Optional[str] = Field(default="")
    hiring_date: Optional[str] = Field(default="")
    salary: Optional[str] = Field(default="")
    emergency_contact: Optional[str] = Field(default="", max_length=200)
    manager_name: Optional[str] = Field(default="", max_length=100)
    employment_status: Optional[str] = Field(default="Active")
    notes: Optional[str] = Field(default="", max_length=1000)


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    department: Optional[str] = Field(None, max_length=100)
    position: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    national_id: Optional[str] = Field(None, max_length=50)
    date_of_birth: Optional[str] = None
    hiring_date: Optional[str] = None
    salary: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=200)
    manager_name: Optional[str] = Field(None, max_length=100)
    employment_status: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=1000)


class EmployeeResponse(BaseModel):
    employee_id: str
    full_name: str
    department: str
    position: str
    email: str
    phone_number: str
    address: str
    national_id: str
    date_of_birth: str
    hiring_date: str
    salary: str
    emergency_contact: str
    manager_name: str
    employment_status: str
    notes: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class EmployeeListResponse(BaseModel):
    total: int
    employees: List[EmployeeResponse]
