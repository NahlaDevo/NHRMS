from pydantic import BaseModel, Field
from typing import Optional
from datetime import date


class EmployeeModel(BaseModel):
    employee_id: str = Field(alias="Employee ID")
    full_name: str = Field(alias="Full Name", min_length=1, max_length=200)
    department: str = Field(alias="Department")
    position: str = Field(alias="Position")
    email: str = Field(alias="Email")
    phone_number: str = Field(alias="Phone Number")
    address: str = Field(alias="Address", default="")
    national_id: str = Field(alias="National ID", default="")
    date_of_birth: str = Field(alias="Date of Birth", default="")
    hiring_date: str = Field(alias="Hiring Date", default="")
    salary: str = Field(alias="Salary", default="")
    emergency_contact: str = Field(alias="Emergency Contact", default="")
    manager_name: str = Field(alias="Manager Name", default="")
    employment_status: str = Field(alias="Employment Status", default="Active")
    notes: str = Field(alias="Notes", default="")
    created_at: str = Field(alias="Created At", default="")
    updated_at: str = Field(alias="Updated At", default="")

    class Config:
        populate_by_name = True
