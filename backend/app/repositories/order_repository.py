from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Product, UserBehavior


def get_order(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def get_user_order(db: Session, *, user_id: int, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id, Order.user_id == user_id).one_or_none()


def list_user_orders(db: Session, *, user_id: int, page: int, page_size: int) -> tuple[list[Order], int]:
    query = db.query(Order).filter(Order.user_id == user_id)
    total = query.count()
    items = (
        query.order_by(Order.created_at.desc(), Order.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def list_order_items(db: Session, *, order_id: int) -> list[OrderItem]:
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).order_by(OrderItem.id.asc()).all()


def create_purchase_behavior(db: Session, *, user_id: int, product_id: int) -> UserBehavior:
    behavior = UserBehavior(
        user_id=user_id,
        session_id=f"user-{user_id}",
        product_id=product_id,
        behavior_type="purchase",
        weight=5,
    )
    db.add(behavior)
    db.flush()
    return behavior

