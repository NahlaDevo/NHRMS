from pydantic import BaseModel, Field, field_validator
from typing import Optional

VALID_ROLES = ["ADMIN", "RECRUITER", "HR", "PAYROLL_MANAGER", "EMPLOYEE"]


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    email: str = Field(..., max_length=200)
    role: Optional[str] = Field(default="EMPLOYEE")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        if v.upper() not in VALID_ROLES:
            raise ValueError(f"Invalid role '{v}'. Must be one of: {VALID_ROLES}")
        return v.upper()


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    refresh_token: str = ""


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    username: str
    email: str
    role: str
    is_active: str
    created_at: str

    class Config:
        from_attributes = True
