from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class CategoryPublic(BaseModel):
    id: int
    name: str
    parent_id: int
    sort_order: int
    status: str

    model_config = {"from_attributes": True}


class ProductListItem(BaseModel):
    id: int
    category_id: int
    name: str
    subtitle: str | None = None
    main_image: str | None = None
    price: Decimal
    stock: int
    sales_count: int
    status: str

    model_config = {"from_attributes": True}


class ProductDetail(ProductListItem):
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    parent_id: int = 0
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    parent_id: int | None = None
    sort_order: int | None = None


class StatusUpdate(BaseModel):
    status: str


class ProductCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=100)
    subtitle: str | None = Field(default=None, max_length=255)
    main_image: str | None = Field(default=None, max_length=255)
    price: Decimal
    stock: int = Field(ge=0)
    description: str | None = None
    status: str = "on_sale"


class ProductUpdate(BaseModel):
    category_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=100)
    subtitle: str | None = Field(default=None, max_length=255)
    main_image: str | None = Field(default=None, max_length=255)
    price: Decimal | None = None
    stock: int | None = Field(default=None, ge=0)
    description: str | None = None
    status: str | None = None
