from decimal import Decimal

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Category, Product, UserBehavior


def list_enabled_categories(db: Session) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.status == "enabled")
        .order_by(Category.sort_order.asc(), Category.id.asc())
        .all()
    )


def list_products(
    db: Session,
    *,
    keyword: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Product], int]:
    query = db.query(Product).filter(Product.status == "on_sale")
    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(or_(Product.name.like(pattern), Product.subtitle.like(pattern)))
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    items = (
        query.order_by(Product.sales_count.desc(), Product.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total


def get_visible_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id, Product.status == "on_sale").one_or_none()


def list_hot_products(db: Session, *, limit: int = 10) -> list[Product]:
    return (
        db.query(Product)
        .filter(Product.status == "on_sale")
        .order_by(Product.sales_count.desc(), Product.id.asc())
        .limit(limit)
        .all()
    )


def create_view_behavior(db: Session, *, user_id: int, product_id: int) -> UserBehavior:
    behavior = UserBehavior(
        user_id=user_id,
        session_id=f"user-{user_id}",
        product_id=product_id,
        behavior_type="view",
        weight=1,
    )
    db.add(behavior)
    db.flush()
    return behavior

