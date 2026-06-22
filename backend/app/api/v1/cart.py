from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartPublic
from app.schemas.common import ApiResponse
from app.services import cart_service

router = APIRouter(prefix="/cart")


@router.get("", response_model=ApiResponse[CartPublic])
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CartPublic]:
    return ApiResponse(data=cart_service.get_cart(db, current_user=current_user))


@router.post("/items", response_model=ApiResponse[CartPublic])
def add_cart_item(
    payload: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CartPublic]:
    return ApiResponse(
        data=cart_service.add_to_cart(
            db,
            current_user=current_user,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
    )


@router.put("/items/{cart_item_id}", response_model=ApiResponse[CartPublic])
def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CartPublic]:
    return ApiResponse(
        data=cart_service.update_cart_item(
            db,
            current_user=current_user,
            cart_item_id=cart_item_id,
            quantity=payload.quantity,
            selected=payload.selected,
        )
    )


@router.delete("/items/{cart_item_id}", response_model=ApiResponse[CartPublic])
def delete_cart_item(
    cart_item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ApiResponse[CartPublic]:
    return ApiResponse(
        data=cart_service.delete_cart_item(
            db, current_user=current_user, cart_item_id=cart_item_id
        )
    )

