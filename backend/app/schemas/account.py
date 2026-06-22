from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=6, max_length=72)
    phone: str | None = Field(default=None, max_length=20)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=72)


class UserPublic(BaseModel):
    id: int
    username: str
    phone: str | None = None
    email: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None
    balance: Decimal
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class LoginResult(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic
