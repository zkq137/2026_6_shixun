from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_optional_current_user
from app.models import User
from app.schemas.common import ApiResponse, PageResponse
from app.schemas.product import CategoryPublic, ProductDetail, ProductListItem
from app.schemas.review import ReviewCreate, ReviewPublic, ReviewSummary
from app.services import product_service, review_service

router = APIRouter()


@router.get("/categories", response_model=ApiResponse[list[CategoryPublic]])
def list_categories(db: Session = Depends(get_db)) -> ApiResponse[list[CategoryPublic]]:
    categories = product_service.get_categories(db)
    return ApiResponse(data=[CategoryPublic.model_validate(item) for item in categories])


@router.get("/products", response_model=ApiResponse[PageResponse[ProductListItem]])
def list_products(
    keyword: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    min_price: Decimal | None = Query(default=None),
    max_price: Decimal | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[ProductListItem]]:
    items, total = product_service.get_products(
        db,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )
    return ApiResponse(
        data=PageResponse(
            items=[ProductListItem.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )


@router.get("/products/hot", response_model=ApiResponse[list[ProductListItem]])
def hot_products(
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ProductListItem]]:
    products = product_service.get_hot_products(db, limit=limit)
    return ApiResponse(data=[ProductListItem.model_validate(item) for item in products])


@router.get("/products/{product_id}", response_model=ApiResponse[ProductDetail])
def product_detail(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_current_user),
) -> ApiResponse[ProductDetail]:
    product = product_service.get_product_detail(db, product_id=product_id, current_user=current_user)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return ApiResponse(data=ProductDetail.model_validate(product))


@router.get("/products/{product_id}/reviews", response_model=ApiResponse[dict])
def product_reviews(
    product_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> ApiResponse[dict]:
    items, total, summary = review_service.list_product_reviews(db, product_id=product_id, page=page, page_size=page_size)
    return ApiResponse(
        data={
            "items": [item.model_dump() for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "summary": summary.model_dump(),
        }
    )


@router.post("/products/{product_id}/reviews", response_model=ApiResponse[ReviewPublic])
def create_product_review(
    product_id: int,
    payload: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[ReviewPublic]:
    return ApiResponse(data=review_service.create_review(db, product_id=product_id, current_user=current_user, payload=payload))
