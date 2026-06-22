from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Product, User
from app.repositories import cart_repository, product_repository
from app.schemas.cart import CartItemPublic, CartPublic


def _to_cart_public(rows) -> CartPublic:
    items = []
    total = Decimal("0.00")
    for cart_item, product in rows:
        subtotal = Decimal(product.price) * cart_item.quantity
        total += subtotal
        items.append(
            CartItemPublic(
                id=cart_item.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.main_image,
                price=product.price,
                stock=product.stock,
                quantity=cart_item.quantity,
                selected=bool(cart_item.selected),
                subtotal=subtotal,
            )
        )
    return CartPublic(items=items, total_amount=total)


def get_cart(db: Session, *, current_user: User) -> CartPublic:
    return _to_cart_public(cart_repository.list_user_cart_items(db, user_id=current_user.id))


def add_to_cart(db: Session, *, current_user: User, product_id: int, quantity: int) -> CartPublic:
    product = product_repository.get_visible_product(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if quantity > product.stock:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")

    cart_item = cart_repository.get_user_cart_product(db, user_id=current_user.id, product_id=product_id)
    if cart_item:
        new_quantity = cart_item.quantity + quantity
        if new_quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")
        cart_item.quantity = new_quantity
        cart_item.selected = 1
    else:
        cart_repository.add_cart_item(db, user_id=current_user.id, product_id=product_id, quantity=quantity)

    cart_repository.create_cart_behavior(db, user_id=current_user.id, product_id=product_id)
    db.commit()
    return get_cart(db, current_user=current_user)


def update_cart_item(
    db: Session,
    *,
    current_user: User,
    cart_item_id: int,
    quantity: int | None,
    selected: bool | None,
) -> CartPublic:
    cart_item = cart_repository.get_user_cart_item(db, user_id=current_user.id, cart_item_id=cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    product = db.get(Product, cart_item.product_id)
    if not product or product.status != "on_sale":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if quantity is not None:
        if quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")
        cart_item.quantity = quantity
    if selected is not None:
        cart_item.selected = 1 if selected else 0
    db.commit()
    return get_cart(db, current_user=current_user)


def delete_cart_item(db: Session, *, current_user: User, cart_item_id: int) -> CartPublic:
    cart_item = cart_repository.get_user_cart_item(db, user_id=current_user.id, cart_item_id=cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
    db.delete(cart_item)
    db.commit()
    return get_cart(db, current_user=current_user)

