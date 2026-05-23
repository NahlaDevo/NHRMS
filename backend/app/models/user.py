from pydantic import BaseModel, Field
from typing import Optional


class UserModel(BaseModel):
    username: str = Field(alias="Username")
    password_hash: str = Field(alias="Password Hash", default="")
    email: str = Field(alias="Email", default="")
    role: str = Field(alias="Role", default="employee")
    is_active: str = Field(alias="Is Active", default="True")
    created_at: str = Field(alias="Created At", default="")
    updated_at: str = Field(alias="Updated At", default="")

    class Config:
        populate_by_name = True
