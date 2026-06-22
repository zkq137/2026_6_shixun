from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.common import ApiResponse, PageResponse
from app.schemas.order import OrderCreate, OrderCreateResult, OrderSummary, PaymentResult
from app.services import order_service

router = APIRouter(prefix="/orders")


@router.post("", response_model=ApiResponse[OrderCreateResult])
def create_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[OrderCreateResult]:
    return ApiResponse(
        data=order_service.create_order(
            db,
            current_user=current_user,
            cart_item_ids=payload.cart_item_ids,
            receiver_name=payload.receiver_name,
            receiver_phone=payload.receiver_phone,
            receiver_address=payload.receiver_address,
            remark=payload.remark,
        )
    )


@router.get("", response_model=ApiResponse[PageResponse[OrderSummary]])
def list_orders(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[OrderSummary]]:
    items, total = order_service.list_orders(
        db, current_user=current_user, page=page, page_size=page_size
    )
    return ApiResponse(data=PageResponse(items=items, total=total, page=page, page_size=page_size))


@router.get("/{order_id}", response_model=ApiResponse[OrderSummary])
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[OrderSummary]:
    return ApiResponse(
        data=order_service.get_order_detail(db, current_user=current_user, order_id=order_id)
    )


@router.post("/{order_id}/pay", response_model=ApiResponse[PaymentResult])
def pay_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[PaymentResult]:
    return ApiResponse(data=order_service.pay_order(db, current_user=current_user, order_id=order_id))


@router.put("/{order_id}/cancel", response_model=ApiResponse[PaymentResult])
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[PaymentResult]:
    return ApiResponse(
        data=order_service.cancel_order(db, current_user=current_user, order_id=order_id)
    )

