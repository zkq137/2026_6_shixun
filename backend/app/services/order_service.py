from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Cart, Order, OrderItem, Product, User
from app.repositories import cart_repository, order_repository
from app.schemas.order import OrderCreateResult, OrderItemPublic, OrderSummary, PaymentResult


def _build_order_no(user_id: int) -> str:
    return f"{datetime.now():%Y%m%d%H%M%S%f}{user_id}"


def _order_to_summary(db: Session, order: Order) -> OrderSummary:
    items = order_repository.list_order_items(db, order_id=order.id)
    return OrderSummary(
        id=order.id,
        order_no=order.order_no,
        total_amount=order.total_amount,
        status=order.status,
        receiver_name=order.receiver_name,
        receiver_phone=order.receiver_phone,
        receiver_address=order.receiver_address,
        remark=order.remark,
        created_at=order.created_at,
        items=[OrderItemPublic.model_validate(item) for item in items],
    )


def create_order(
    db: Session,
    *,
    current_user: User,
    cart_item_ids: list[int],
    receiver_name: str,
    receiver_phone: str,
    receiver_address: str,
    remark: str | None,
) -> OrderCreateResult:
    cart_items: list[Cart] = []
    for cart_item_id in cart_item_ids:
        cart_item = cart_repository.get_user_cart_item(
            db, user_id=current_user.id, cart_item_id=cart_item_id
        )
        if not cart_item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        cart_items.append(cart_item)

    if not cart_items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No cart items selected")

    products: dict[int, Product] = {}
    total_amount = Decimal("0.00")
    for cart_item in cart_items:
        product = db.get(Product, cart_item.product_id)
        if not product or product.status != "on_sale":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        if cart_item.quantity > product.stock:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient stock")
        products[cart_item.product_id] = product
        total_amount += Decimal(product.price) * cart_item.quantity

    order = Order(
        order_no=_build_order_no(current_user.id),
        user_id=current_user.id,
        total_amount=total_amount,
        status="pending",
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        receiver_address=receiver_address,
        remark=remark,
    )
    db.add(order)
    db.flush()

    for cart_item in cart_items:
        product = products[cart_item.product_id]
        subtotal = Decimal(product.price) * cart_item.quantity
        product.stock -= cart_item.quantity
        product.sales_count += cart_item.quantity
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.main_image,
                price=product.price,
                quantity=cart_item.quantity,
                subtotal=subtotal,
            )
        )
        order_repository.create_purchase_behavior(
            db, user_id=current_user.id, product_id=product.id
        )

    cart_repository.delete_cart_items(db, cart_items)
    db.commit()
    db.refresh(order)
    return OrderCreateResult(
        order_id=order.id,
        order_no=order.order_no,
        total_amount=order.total_amount,
        status=order.status,
    )


def list_orders(db: Session, *, current_user: User, page: int, page_size: int):
    orders, total = order_repository.list_user_orders(
        db, user_id=current_user.id, page=page, page_size=page_size
    )
    return [_order_to_summary(db, order) for order in orders], total


def get_order_detail(db: Session, *, current_user: User, order_id: int) -> OrderSummary:
    order = order_repository.get_user_order(db, user_id=current_user.id, order_id=order_id)
    if not order:
        if order_repository.get_order(db, order_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return _order_to_summary(db, order)


def pay_order(db: Session, *, current_user: User, order_id: int) -> PaymentResult:
    order = order_repository.get_user_order(db, user_id=current_user.id, order_id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order cannot be paid")
    if Decimal(current_user.balance) < Decimal(order.total_amount):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Insufficient balance")

    current_user.balance = Decimal(current_user.balance) - Decimal(order.total_amount)
    order.status = "paid"
    db.commit()
    db.refresh(order)
    db.refresh(current_user)
    return PaymentResult(
        order_id=order.id,
        order_no=order.order_no,
        status=order.status,
        balance=current_user.balance,
    )


def cancel_order(db: Session, *, current_user: User, order_id: int) -> PaymentResult:
    order = order_repository.get_user_order(db, user_id=current_user.id, order_id=order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    if order.status not in {"pending", "paid"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Order cannot be cancelled")

    items = order_repository.list_order_items(db, order_id=order.id)
    for item in items:
        product = db.get(Product, item.product_id)
        if product:
            product.stock += item.quantity
            product.sales_count = max(0, product.sales_count - item.quantity)

    if order.status == "paid":
        current_user.balance = Decimal(current_user.balance) + Decimal(order.total_amount)
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    db.refresh(current_user)
    return PaymentResult(
        order_id=order.id,
        order_no=order.order_no,
        status=order.status,
        balance=current_user.balance,
    )

