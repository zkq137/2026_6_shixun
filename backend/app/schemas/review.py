from datetime import datetime

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    content: str = Field(min_length=1, max_length=1000)
    is_anonymous: bool = False


class ReviewPublic(BaseModel):
    id: int
    product_id: int
    user_id: int
    username: str
    nickname: str | None = None
    rating: int
    content: str
    is_anonymous: bool
    is_purchased: bool
    status: str
    created_at: datetime | None = None


class AdminReviewPublic(ReviewPublic):
    product_name: str
    order_id: int | None = None
    updated_at: datetime | None = None


class ReviewSummary(BaseModel):
    total: int
    average_rating: float


class ReviewStatusUpdate(BaseModel):
    status: str = Field(pattern="^(visible|hidden)$")
