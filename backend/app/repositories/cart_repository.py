from sqlalchemy.orm import Session

from app.models import Cart, Product, UserBehavior


def get_cart_item(db: Session, cart_item_id: int) -> Cart | None:
    return db.get(Cart, cart_item_id)


def get_user_cart_item(db: Session, *, user_id: int, cart_item_id: int) -> Cart | None:
    return db.query(Cart).filter(Cart.id == cart_item_id, Cart.user_id == user_id).one_or_none()


def get_user_cart_product(db: Session, *, user_id: int, product_id: int) -> Cart | None:
    return db.query(Cart).filter(Cart.user_id == user_id, Cart.product_id == product_id).one_or_none()


def list_user_cart_items(db: Session, *, user_id: int) -> list[tuple[Cart, Product]]:
    return (
        db.query(Cart, Product)
        .join(Product, Product.id == Cart.product_id)
        .filter(Cart.user_id == user_id)
        .order_by(Cart.id.asc())
        .all()
    )


def add_cart_item(db: Session, *, user_id: int, product_id: int, quantity: int) -> Cart:
    cart_item = Cart(user_id=user_id, product_id=product_id, quantity=quantity, selected=1)
    db.add(cart_item)
    db.flush()
    return cart_item


def delete_cart_items(db: Session, cart_items: list[Cart]) -> None:
    for item in cart_items:
        db.delete(item)


def create_cart_behavior(db: Session, *, user_id: int, product_id: int) -> UserBehavior:
    behavior = UserBehavior(
        user_id=user_id,
        session_id=f"user-{user_id}",
        product_id=product_id,
        behavior_type="cart",
        weight=3,
    )
    db.add(behavior)
    db.flush()
    return behavior

