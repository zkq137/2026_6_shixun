from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class InventoryAlertPublic(BaseModel):
    id: int
    product_id: int
    current_stock: int
    predicted_sales: int
    risk_level: str
    suggestion: str
    status: str

    model_config = {"from_attributes": True}


class SalesStatisticPublic(BaseModel):
    product_id: int
    stat_date: date
    sales_count: int
    sales_amount: Decimal

    model_config = {"from_attributes": True}


class SalesPredictRequest(BaseModel):
    product_id: int
    days: int = 7


class SalesPredictionPublic(BaseModel):
    product_id: int
    predict_date: date
    predicted_count: int
    method: str
    basis: str | None = None

    model_config = {"from_attributes": True}
