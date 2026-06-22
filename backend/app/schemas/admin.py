from datetime import datetime

from pydantic import BaseModel, Field
from decimal import Decimal


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


class DashboardStats(BaseModel):
    today_sales_amount: Decimal
    today_order_count: int
    user_count: int
    inventory_alert_count: int


class AdminUserPublic(BaseModel):
    id: int
    username: str
    phone: str | None = None
    email: str | None = None
    nickname: str | None = None
    balance: Decimal
    status: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}
