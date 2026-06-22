from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Category, Product, User
from app.repositories import product_repository


def get_categories(db: Session) -> list[Category]:
    return product_repository.list_enabled_categories(db)


def get_products(
    db: Session,
    *,
    keyword: str | None = None,
    category_id: int | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[Product], int]:
    return product_repository.list_products(
        db,
        keyword=keyword,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        page=page,
        page_size=page_size,
    )


def get_product_detail(db: Session, *, product_id: int, current_user: User | None = None) -> Product | None:
    product = product_repository.get_visible_product(db, product_id)
    if product and current_user:
        try:
            product_repository.create_view_behavior(db, user_id=current_user.id, product_id=product.id)
            db.commit()
        except Exception:
            db.rollback()
    return product


def get_hot_products(db: Session, *, limit: int = 10) -> list[Product]:
    return product_repository.list_hot_products(db, limit=limit)

