from datetime import date, timedelta
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Category, InventoryAlert, Order, Product, SalesPrediction, SalesStatistic, User
from app.schemas.admin import DashboardStats
from app.schemas.product import CategoryCreate, CategoryUpdate, ProductCreate, ProductUpdate


def dashboard(db: Session) -> DashboardStats:
    today = date.today()
    amount = (
        db.query(func.coalesce(func.sum(Order.total_amount), 0))
        .filter(func.date(Order.created_at) == today)
        .scalar()
    )
    order_count = db.query(Order).filter(func.date(Order.created_at) == today).count()
    user_count = db.query(User).count()
    alert_count = db.query(InventoryAlert).filter(InventoryAlert.status == "open").count()
    return DashboardStats(
        today_sales_amount=Decimal(amount or 0),
        today_order_count=order_count,
        user_count=user_count,
        inventory_alert_count=alert_count,
    )


def list_admin_products(db: Session, page: int, page_size: int, keyword: str | None, status_value: str | None):
    query = db.query(Product)
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if status_value:
        query = query.filter(Product.status == status_value)
    total = query.count()
    items = query.order_by(Product.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def create_product(db: Session, payload: ProductCreate) -> Product:
    if not db.get(Category, payload.category_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, payload: ProductUpdate) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    data = payload.model_dump(exclude_unset=True)
    if "category_id" in data and not db.get(Category, data["category_id"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for key, value in data.items():
        setattr(product, key, value)
    db.commit()
    db.refresh(product)
    return product


def update_product_status(db: Session, product_id: int, status_value: str) -> Product:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    product.status = status_value
    db.commit()
    db.refresh(product)
    return product


def list_categories(db: Session):
    return db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc()).all()


def create_category(db: Session, payload: CategoryCreate) -> Category:
    category = Category(**payload.model_dump(), status="enabled")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category_id: int, payload: CategoryUpdate) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    db.commit()
    db.refresh(category)
    return category


def update_category_status(db: Session, category_id: int, status_value: str) -> Category:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    category.status = status_value
    db.commit()
    db.refresh(category)
    return category


def list_admin_orders(db: Session, page: int, page_size: int, status_value: str | None):
    query = db.query(Order)
    if status_value:
        query = query.filter(Order.status == status_value)
    total = query.count()
    items = query.order_by(Order.created_at.desc(), Order.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def get_admin_order(db: Session, order_id: int) -> Order:
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


def update_order_status(db: Session, order_id: int, status_value: str) -> Order:
    order = get_admin_order(db, order_id)
    order.status = status_value
    db.commit()
    db.refresh(order)
    return order


def list_users(db: Session, page: int, page_size: int, keyword: str | None, status_value: str | None):
    query = db.query(User)
    if keyword:
        query = query.filter(User.username.like(f"%{keyword}%"))
    if status_value:
        query = query.filter(User.status == status_value)
    total = query.count()
    items = query.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def update_user_status(db: Session, user_id: int, status_value: str) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.status = status_value
    db.commit()
    db.refresh(user)
    return user


def list_inventory_alerts(db: Session, page: int, page_size: int, status_value: str | None):
    query = db.query(InventoryAlert)
    if status_value:
        query = query.filter(InventoryAlert.status == status_value)
    total = query.count()
    items = query.order_by(InventoryAlert.created_at.desc(), InventoryAlert.id.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def update_inventory_alert_status(db: Session, alert_id: int, status_value: str) -> InventoryAlert:
    alert = db.get(InventoryAlert, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory alert not found")
    alert.status = status_value
    db.commit()
    db.refresh(alert)
    return alert


def list_sales_statistics(db: Session, product_id: int | None, start_date: date | None, end_date: date | None):
    query = db.query(SalesStatistic)
    if product_id:
        query = query.filter(SalesStatistic.product_id == product_id)
    if start_date:
        query = query.filter(SalesStatistic.stat_date >= start_date)
    if end_date:
        query = query.filter(SalesStatistic.stat_date <= end_date)
    return query.order_by(SalesStatistic.stat_date.desc()).limit(500).all()


def predict_sales(db: Session, product_id: int, days: int) -> SalesPrediction:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    start = date.today() - timedelta(days=days - 1)
    rows = db.query(SalesStatistic).filter(SalesStatistic.product_id == product_id, SalesStatistic.stat_date >= start).all()
    predicted = round(sum(row.sales_count for row in rows) / max(days, 1)) if rows else 0
    prediction = SalesPrediction(
        product_id=product_id,
        predict_date=date.today() + timedelta(days=1),
        predicted_count=predicted,
        method="moving_average",
        basis=f"Based on recent {days} days average sales.",
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
