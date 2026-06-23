from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Order, OrderItem, Product, ProductReview, User
from app.schemas.review import AdminReviewPublic, ReviewCreate, ReviewPublic, ReviewSummary


def _to_public(review: ProductReview, user: User, *, product_name: str | None = None) -> ReviewPublic:
    username = "匿名用户" if review.is_anonymous else user.username
    nickname = None if review.is_anonymous else user.nickname
    data = {
        "id": review.id,
        "product_id": review.product_id,
        "user_id": review.user_id,
        "username": username,
        "nickname": nickname,
        "rating": review.rating,
        "content": review.content,
        "is_anonymous": bool(review.is_anonymous),
        "is_purchased": bool(review.is_purchased),
        "status": review.status,
        "created_at": review.created_at,
    }
    if product_name is not None:
        return AdminReviewPublic(
            **data,
            product_name=product_name,
            order_id=review.order_id,
            updated_at=review.updated_at,
        )
    return ReviewPublic(**data)


def _get_purchase_order_id(db: Session, *, user_id: int, product_id: int) -> int | None:
    row = (
        db.query(Order.id)
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(
            Order.user_id == user_id,
            OrderItem.product_id == product_id,
            Order.status.in_(["paid", "shipped", "completed"]),
        )
        .order_by(Order.created_at.desc(), Order.id.desc())
        .first()
    )
    return row[0] if row else None


def list_product_reviews(db: Session, *, product_id: int, page: int, page_size: int):
    if not db.get(Product, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    query = (
        db.query(ProductReview, User)
        .join(User, User.id == ProductReview.user_id)
        .filter(ProductReview.product_id == product_id, ProductReview.status == "visible")
    )
    total = query.count()
    rows = (
        query.order_by(ProductReview.created_at.desc(), ProductReview.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    items = [_to_public(review, user) for review, user in rows]
    average = (
        db.query(func.coalesce(func.avg(ProductReview.rating), 0))
        .filter(ProductReview.product_id == product_id, ProductReview.status == "visible")
        .scalar()
    )
    return items, total, ReviewSummary(total=total, average_rating=round(float(average or 0), 1))


def create_review(db: Session, *, product_id: int, current_user: User, payload: ReviewCreate) -> ReviewPublic:
    if not db.get(Product, product_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="评论内容不能为空")

    order_id = _get_purchase_order_id(db, user_id=current_user.id, product_id=product_id)
    review = ProductReview(
        product_id=product_id,
        user_id=current_user.id,
        order_id=order_id,
        rating=payload.rating,
        content=content,
        is_anonymous=1 if payload.is_anonymous else 0,
        is_purchased=1 if order_id else 0,
        status="visible",
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return _to_public(review, current_user)


def list_admin_reviews(
    db: Session,
    *,
    page: int,
    page_size: int,
    product_id: int | None,
    user_id: int | None,
    status_value: str | None,
):
    query = db.query(ProductReview, User, Product).join(User, User.id == ProductReview.user_id).join(
        Product, Product.id == ProductReview.product_id
    )
    if product_id:
        query = query.filter(ProductReview.product_id == product_id)
    if user_id:
        query = query.filter(ProductReview.user_id == user_id)
    if status_value:
        query = query.filter(ProductReview.status == status_value)

    total = query.count()
    rows = (
        query.order_by(ProductReview.created_at.desc(), ProductReview.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [_to_public(review, user, product_name=product.name) for review, user, product in rows], total


def update_review_status(db: Session, *, review_id: int, status_value: str) -> AdminReviewPublic:
    if status_value not in {"visible", "hidden"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid review status")
    row = (
        db.query(ProductReview, User, Product)
        .join(User, User.id == ProductReview.user_id)
        .join(Product, Product.id == ProductReview.product_id)
        .filter(ProductReview.id == review_id)
        .one_or_none()
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    review, user, product = row
    review.status = status_value
    db.commit()
    db.refresh(review)
    return _to_public(review, user, product_name=product.name)
