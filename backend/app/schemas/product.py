from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


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

