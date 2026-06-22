from datetime import datetime

from pydantic import BaseModel, Field


class AdminLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)


class AdminPublic(BaseModel):
    id: int
    username: str
    role: str
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminLoginResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminPublic

