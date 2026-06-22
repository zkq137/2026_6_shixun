from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int | None = Field(default=None, ge=1)
    selected: bool | None = None


class CartItemPublic(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_image: str | None = None
    price: Decimal
    stock: int
    quantity: int
    selected: bool
    subtotal: Decimal


class CartPublic(BaseModel):
    items: list[CartItemPublic]
    total_amount: Decimal

