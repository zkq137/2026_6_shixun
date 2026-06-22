from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    cart_item_ids: list[int] = Field(min_length=1)
    receiver_name: str = Field(min_length=1, max_length=50)
    receiver_phone: str = Field(min_length=1, max_length=20)
    receiver_address: str = Field(min_length=1, max_length=255)
    remark: str | None = Field(default=None, max_length=255)


class OrderItemPublic(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: str | None = None
    price: Decimal
    quantity: int
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderSummary(BaseModel):
    id: int
    order_no: str
    total_amount: Decimal
    status: str
    receiver_name: str
    receiver_phone: str
    receiver_address: str
    remark: str | None = None
    created_at: datetime | None = None
    items: list[OrderItemPublic] = []

    model_config = {"from_attributes": True}


class OrderCreateResult(BaseModel):
    order_id: int
    order_no: str
    total_amount: Decimal
    status: str


class PaymentResult(BaseModel):
    order_id: int
    order_no: str
    status: str
    balance: Decimal

