from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models import Category, InventoryAlert, Order, User


client = TestClient(app)


def admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def user_headers() -> dict[str, str]:
    username = f"admin_guard_{uuid4().hex[:10]}"
    client.post("/api/auth/register", json={"username": username, "password": "test123456"})
    response = client.post("/api/auth/login", json={"username": username, "password": "test123456"})
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_dashboard_and_user_forbidden() -> None:
    forbidden = client.get("/api/admin/dashboard", headers=user_headers())
    assert forbidden.status_code == 401

    response = client.get("/api/admin/dashboard", headers=admin_headers())
    assert response.status_code == 200
    data = response.json()["data"]
    assert "today_sales_amount" in data
    assert "today_order_count" in data
    assert "user_count" in data
    assert "inventory_alert_count" in data


def test_admin_category_and_product_crud() -> None:
    headers = admin_headers()
    category_name = f"测试分类{uuid4().hex[:6]}"

    create_category = client.post(
        "/api/admin/categories",
        headers=headers,
        json={"name": category_name, "sort_order": 99},
    )
    assert create_category.status_code == 200
    category_id = create_category.json()["data"]["id"]

    update_category = client.put(
        f"/api/admin/categories/{category_id}",
        headers=headers,
        json={"name": category_name + "改"},
    )
    assert update_category.status_code == 200

    disable_category = client.put(
        f"/api/admin/categories/{category_id}/status",
        headers=headers,
        json={"status": "disabled"},
    )
    assert disable_category.status_code == 200
    assert disable_category.json()["data"]["status"] == "disabled"

    product_name = f"测试商品{uuid4().hex[:6]}"
    create_product = client.post(
        "/api/admin/products",
        headers=headers,
        json={
            "category_id": category_id,
            "name": product_name,
            "subtitle": "后台测试",
            "main_image": "/images/products/test.jpg",
            "price": "12.50",
            "stock": 20,
            "description": "测试商品描述",
            "status": "on_sale",
        },
    )
    assert create_product.status_code == 200
    product_id = create_product.json()["data"]["id"]

    list_products = client.get("/api/admin/products", headers=headers, params={"keyword": product_name})
    assert list_products.status_code == 200
    assert list_products.json()["data"]["total"] >= 1

    update_product = client.put(
        f"/api/admin/products/{product_id}",
        headers=headers,
        json={"price": "15.00", "stock": 18},
    )
    assert update_product.status_code == 200
    assert Decimal(update_product.json()["data"]["price"]) == Decimal("15.00")

    off_sale = client.put(
        f"/api/admin/products/{product_id}/status",
        headers=headers,
        json={"status": "off_sale"},
    )
    assert off_sale.status_code == 200
    assert off_sale.json()["data"]["status"] == "off_sale"

    delete_product = client.delete(f"/api/admin/products/{product_id}", headers=headers)
    assert delete_product.status_code == 200
    assert delete_product.json()["data"]["status"] == "off_sale"


def test_admin_orders_users_inventory_and_sales() -> None:
    headers = admin_headers()

    orders = client.get("/api/admin/orders", headers=headers)
    assert orders.status_code == 200
    if orders.json()["data"]["total"] > 0:
        order_id = orders.json()["data"]["items"][0]["id"]
        detail = client.get(f"/api/admin/orders/{order_id}", headers=headers)
        assert detail.status_code == 200
        update = client.put(
            f"/api/admin/orders/{order_id}/status",
            headers=headers,
            json={"status": "shipped"},
        )
        assert update.status_code == 200
        assert update.json()["data"]["status"] == "shipped"

    users = client.get("/api/admin/users", headers=headers)
    assert users.status_code == 200
    assert users.json()["data"]["total"] >= 1
    user_id = users.json()["data"]["items"][0]["id"]
    disabled = client.put(
        f"/api/admin/users/{user_id}/status",
        headers=headers,
        json={"status": "disabled"},
    )
    assert disabled.status_code == 200
    assert disabled.json()["data"]["status"] == "disabled"
    client.put(f"/api/admin/users/{user_id}/status", headers=headers, json={"status": "normal"})

    alerts = client.get("/api/admin/inventory/alerts", headers=headers)
    assert alerts.status_code == 200
    if alerts.json()["data"]["total"] > 0:
        alert_id = alerts.json()["data"]["items"][0]["id"]
        handled = client.put(
            f"/api/admin/inventory/alerts/{alert_id}/status",
            headers=headers,
            json={"status": "handled"},
        )
        assert handled.status_code == 200
        assert handled.json()["data"]["status"] == "handled"

    stats = client.get("/api/admin/sales/statistics", headers=headers)
    assert stats.status_code == 200
    assert len(stats.json()["data"]) > 0

    with SessionLocal() as session:
        product_id = session.query(Category).first().id
        order = session.query(Order).first()
        user = session.query(User).first()
        alert = session.query(InventoryAlert).first()
        assert user is not None
        assert order is not None or alert is not None

    predict = client.post(
        "/api/admin/sales/predict",
        headers=headers,
        json={"product_id": 1, "days": 7},
    )
    assert predict.status_code == 200
    assert predict.json()["data"]["method"] == "moving_average"

