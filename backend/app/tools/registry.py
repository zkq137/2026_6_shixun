from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from time import perf_counter
from typing import Any, Callable

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import (
    AgentToolCall,
    Faq,
    InventoryAlert,
    Order,
    OrderItem,
    Product,
    ProductSimilarity,
    SalesPrediction,
    SalesStatistic,
    User,
    UserBehavior,
)

ToolFunction = Callable[[Session, dict[str, Any]], dict[str, Any]]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, ToolFunction] = {}

    def register(self, name: str, func_: ToolFunction):
        self._tools[name] = func_

    def call(
        self,
        db: Session,
        *,
        conversation_id: int | None,
        agent_type: str,
        tool_name: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        started = perf_counter()
        status = "success"
        output: dict[str, Any] | None = None
        error_message: str | None = None
        try:
            output = self._tools[tool_name](db, payload)
            return output
        except Exception as exc:
            status = "failed"
            error_message = str(exc)
            output = {"error": error_message}
            return output
        finally:
            db.add(
                AgentToolCall(
                    conversation_id=conversation_id,
                    agent_type=agent_type,
                    tool_name=tool_name,
                    input_json=payload,
                    output_json=output,
                    status=status,
                    error_message=error_message,
                    duration_ms=int((perf_counter() - started) * 1000),
                )
            )
            db.flush()


def _product_item(product: Product) -> dict[str, Any]:
    return {
        "product_id": product.id,
        "name": product.name,
        "price": float(product.price),
        "stock": product.stock,
        "sales_count": product.sales_count,
        "status": product.status,
    }


def search_products(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    keyword = payload.get("keyword")
    category_id = payload.get("category_id")
    limit = int(payload.get("limit") or 10)
    query = db.query(Product).filter(Product.status == "on_sale")
    if keyword:
        query = query.filter(Product.name.like(f"%{keyword}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    products = query.order_by(Product.sales_count.desc()).limit(limit).all()
    return {"items": [_product_item(product) for product in products]}


def get_product_detail(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    product = db.get(Product, int(payload["product_id"]))
    if not product or product.status != "on_sale":
        return {"found": False}
    item = _product_item(product)
    item["description"] = product.description
    return {"found": True, "product": item}


def get_user_orders(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = int(payload["user_id"])
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .limit(int(payload.get("limit") or 5))
        .all()
    )
    return {
        "items": [
            {
                "order_id": order.id,
                "order_no": order.order_no,
                "status": order.status,
                "total_amount": float(order.total_amount),
            }
            for order in orders
        ]
    }


def get_order_detail(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = payload.get("user_id")
    order = db.get(Order, int(payload["order_id"]))
    if not order or (user_id is not None and order.user_id != int(user_id)):
        return {"found": False}
    items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
    return {
        "found": True,
        "order_id": order.id,
        "order_no": order.order_no,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "items": [
            {
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "subtotal": float(item.subtotal),
            }
            for item in items
        ],
    }


def query_faq(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    question = payload.get("question", "")
    faqs = db.query(Faq).filter(Faq.status == "enabled").all()
    for faq in faqs:
        keywords = [keyword.strip() for keyword in faq.keywords.split(",") if keyword.strip()]
        if faq.question in question or any(keyword in question for keyword in keywords):
            return {"matched": True, "question": faq.question, "answer": faq.answer}
    return {"matched": False}


def get_user_behavior(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    user_id = payload.get("user_id")
    query = db.query(UserBehavior)
    if user_id:
        query = query.filter(UserBehavior.user_id == int(user_id))
    rows = query.order_by(UserBehavior.created_at.desc()).limit(int(payload.get("limit") or 20)).all()
    return {
        "items": [
            {
                "product_id": row.product_id,
                "behavior_type": row.behavior_type,
                "weight": row.weight,
            }
            for row in rows
        ]
    }


def get_similar_products(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    product_id = payload.get("product_id")
    if product_id:
        similarities = (
            db.query(ProductSimilarity)
            .filter(ProductSimilarity.product_id == int(product_id))
            .order_by(ProductSimilarity.score.desc())
            .limit(int(payload.get("limit") or 10))
            .all()
        )
        ids = [row.similar_product_id for row in similarities]
    else:
        behavior = (
            db.query(UserBehavior)
            .filter(UserBehavior.user_id == int(payload["user_id"]), UserBehavior.product_id.isnot(None))
            .order_by(UserBehavior.weight.desc(), UserBehavior.created_at.desc())
            .first()
        )
        ids = [behavior.product_id] if behavior else []
    products = db.query(Product).filter(Product.id.in_(ids), Product.status == "on_sale").all() if ids else []
    return {"items": [_product_item(product) for product in products]}


def get_hot_products(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    products = (
        db.query(Product)
        .filter(Product.status == "on_sale")
        .order_by(Product.sales_count.desc())
        .limit(int(payload.get("limit") or 10))
        .all()
    )
    return {"items": [_product_item(product) for product in products]}


def get_sales_statistics(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    days = int(payload.get("days") or 7)
    start_date = date.today() - timedelta(days=days - 1)
    query = db.query(SalesStatistic).filter(SalesStatistic.stat_date >= start_date)
    if payload.get("product_id"):
        query = query.filter(SalesStatistic.product_id == int(payload["product_id"]))
    rows = query.order_by(SalesStatistic.stat_date.desc()).all()
    total_count = sum(row.sales_count for row in rows)
    total_amount = sum(Decimal(row.sales_amount) for row in rows)
    top_rows = (
        db.query(SalesStatistic.product_id, func.sum(SalesStatistic.sales_count).label("count"))
        .filter(SalesStatistic.stat_date >= start_date)
        .group_by(SalesStatistic.product_id)
        .order_by(func.sum(SalesStatistic.sales_count).desc())
        .limit(5)
        .all()
    )
    return {
        "days": days,
        "total_sales_count": total_count,
        "total_sales_amount": float(total_amount),
        "top_products": [{"product_id": row.product_id, "sales_count": int(row.count)} for row in top_rows],
    }


def predict_product_sales(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    product_id = int(payload["product_id"])
    days = int(payload.get("days") or 7)
    start_date = date.today() - timedelta(days=days - 1)
    rows = (
        db.query(SalesStatistic)
        .filter(SalesStatistic.product_id == product_id, SalesStatistic.stat_date >= start_date)
        .all()
    )
    predicted = round(sum(row.sales_count for row in rows) / max(days, 1)) if rows else 0
    prediction = SalesPrediction(
        product_id=product_id,
        predict_date=date.today() + timedelta(days=1),
        predicted_count=predicted,
        method="moving_average",
        basis=f"Based on recent {days} days average sales.",
    )
    db.add(prediction)
    db.flush()
    return {
        "product_id": product_id,
        "predicted_count": predicted,
        "method": "moving_average",
        "basis": prediction.basis,
    }


def check_inventory_risk(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    product_id = int(payload["product_id"])
    product = db.get(Product, product_id)
    if not product:
        return {"found": False}
    predicted_sales = int(payload.get("predicted_sales") or payload.get("predicted_count") or 0)
    if product.stock < predicted_sales:
        risk = "high"
    elif product.stock < predicted_sales * 1.5:
        risk = "medium"
    else:
        risk = "low"
    return {
        "found": True,
        "product_id": product.id,
        "current_stock": product.stock,
        "predicted_sales": predicted_sales,
        "risk_level": risk,
        "suggestion": f"Suggest replenishing {max(predicted_sales - product.stock + 30, 0)} units.",
    }


def create_inventory_alert(db: Session, payload: dict[str, Any]) -> dict[str, Any]:
    alert = InventoryAlert(
        product_id=int(payload["product_id"]),
        current_stock=int(payload["current_stock"]),
        predicted_sales=int(payload["predicted_sales"]),
        risk_level=payload["risk_level"],
        suggestion=payload["suggestion"],
        status="open",
    )
    db.add(alert)
    db.flush()
    return {"alert_id": alert.id, "status": alert.status}


registry = ToolRegistry()
registry.register("search_products", search_products)
registry.register("get_product_detail", get_product_detail)
registry.register("get_user_orders", get_user_orders)
registry.register("get_order_detail", get_order_detail)
registry.register("query_faq", query_faq)
registry.register("get_user_behavior", get_user_behavior)
registry.register("get_similar_products", get_similar_products)
registry.register("get_hot_products", get_hot_products)
registry.register("get_sales_statistics", get_sales_statistics)
registry.register("predict_product_sales", predict_product_sales)
registry.register("check_inventory_risk", check_inventory_risk)
registry.register("create_inventory_alert", create_inventory_alert)

