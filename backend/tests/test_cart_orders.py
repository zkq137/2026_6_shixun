from decimal import Decimal
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models import Product, User, UserBehavior


client = TestClient(app)


def register_and_login(prefix: str = "buyer") -> tuple[str, dict]:
    username = f"{prefix}_{uuid4().hex[:10]}"
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456"},
    )
    assert register_response.status_code == 200
    assert Decimal(register_response.json()["data"]["balance"]) == Decimal("100000.00")

    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "test123456"},
    )
    assert login_response.status_code == 200
    return login_response.json()["data"]["access_token"], register_response.json()["data"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def first_product_with_stock() -> tuple[int, int, Decimal]:
    with SessionLocal() as session:
        product = (
            session.query(Product)
            .filter(Product.status == "on_sale", Product.stock > 10)
            .order_by(Product.id.asc())
            .first()
        )
        assert product is not None
        return product.id, product.stock, Decimal(product.price)


def test_cart_order_pay_and_cancel_flow() -> None:
    token, _ = register_and_login()
    product_id, stock_before, price = first_product_with_stock()

    add_response = client.post(
        "/api/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": 2},
    )
    assert add_response.status_code == 200
    cart = add_response.json()["data"]
    assert len(cart["items"]) == 1
    assert cart["items"][0]["quantity"] == 2

    add_again_response = client.post(
        "/api/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": 1},
    )
    assert add_again_response.status_code == 200
    cart = add_again_response.json()["data"]
    item = cart["items"][0]
    assert item["quantity"] == 3
    cart_item_id = item["id"]

    update_response = client.put(
        f"/api/cart/items/{cart_item_id}",
        headers=auth_headers(token),
        json={"quantity": 2, "selected": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["data"]["items"][0]["quantity"] == 2

    with SessionLocal() as session:
        cart_behaviors = (
            session.query(UserBehavior)
            .filter(UserBehavior.product_id == product_id, UserBehavior.behavior_type == "cart")
            .count()
        )
    assert cart_behaviors >= 1

    order_response = client.post(
        "/api/orders",
        headers=auth_headers(token),
        json={
            "cart_item_ids": [cart_item_id],
            "receiver_name": "Test Receiver",
            "receiver_phone": "13800000000",
            "receiver_address": "Test Address",
            "remark": "test order",
        },
    )
    assert order_response.status_code == 200
    order_data = order_response.json()["data"]
    assert order_data["status"] == "pending"
    assert Decimal(order_data["total_amount"]) == price * 2
    order_id = order_data["order_id"]

    empty_cart_response = client.get("/api/cart", headers=auth_headers(token))
    assert empty_cart_response.status_code == 200
    assert empty_cart_response.json()["data"]["items"] == []

    with SessionLocal() as session:
        product = session.get(Product, product_id)
        assert product is not None
        assert product.stock == stock_before - 2
        purchase_behaviors = (
            session.query(UserBehavior)
            .filter(UserBehavior.product_id == product_id, UserBehavior.behavior_type == "purchase")
            .count()
        )
    assert purchase_behaviors >= 1

    orders_response = client.get("/api/orders", headers=auth_headers(token))
    assert orders_response.status_code == 200
    assert orders_response.json()["data"]["total"] >= 1

    detail_response = client.get(f"/api/orders/{order_id}", headers=auth_headers(token))
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == order_id

    other_token, _ = register_and_login("other")
    forbidden_response = client.get(f"/api/orders/{order_id}", headers=auth_headers(other_token))
    assert forbidden_response.status_code == 403

    pay_response = client.post(f"/api/orders/{order_id}/pay", headers=auth_headers(token))
    assert pay_response.status_code == 200
    pay_data = pay_response.json()["data"]
    assert pay_data["status"] == "paid"
    assert Decimal(pay_data["balance"]) == Decimal("100000.00") - price * 2

    cancel_response = client.put(f"/api/orders/{order_id}/cancel", headers=auth_headers(token))
    assert cancel_response.status_code == 200
    cancel_data = cancel_response.json()["data"]
    assert cancel_data["status"] == "cancelled"
    assert Decimal(cancel_data["balance"]) == Decimal("100000.00")

    repeat_cancel_response = client.put(f"/api/orders/{order_id}/cancel", headers=auth_headers(token))
    assert repeat_cancel_response.status_code == 409

    with SessionLocal() as session:
        product = session.get(Product, product_id)
        assert product is not None
        assert product.stock == stock_before


def test_delete_cart_item_and_stock_limit() -> None:
    token, _ = register_and_login("cart")
    product_id, stock_before, _ = first_product_with_stock()

    too_many_response = client.post(
        "/api/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": stock_before + 1},
    )
    assert too_many_response.status_code == 409

    add_response = client.post(
        "/api/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": 1},
    )
    assert add_response.status_code == 200
    cart_item_id = add_response.json()["data"]["items"][0]["id"]

    delete_response = client.delete(f"/api/cart/items/{cart_item_id}", headers=auth_headers(token))
    assert delete_response.status_code == 200
    assert delete_response.json()["data"]["items"] == []


def test_pay_order_with_insufficient_balance_fails() -> None:
    token, user_data = register_and_login("poor")
    product_id, _, price = first_product_with_stock()

    add_response = client.post(
        "/api/cart/items",
        headers=auth_headers(token),
        json={"product_id": product_id, "quantity": 1},
    )
    cart_item_id = add_response.json()["data"]["items"][0]["id"]
    order_response = client.post(
        "/api/orders",
        headers=auth_headers(token),
        json={
            "cart_item_ids": [cart_item_id],
            "receiver_name": "Test Receiver",
            "receiver_phone": "13800000000",
            "receiver_address": "Test Address",
        },
    )
    order_id = order_response.json()["data"]["order_id"]

    with SessionLocal() as session:
        user = session.get(User, user_data["id"])
        assert user is not None
        user.balance = Decimal("0.00")
        session.commit()

    pay_response = client.post(f"/api/orders/{order_id}/pay", headers=auth_headers(token))
    assert pay_response.status_code == 409

    # Clean up stock by cancelling the still-pending order.
    cancel_response = client.put(f"/api/orders/{order_id}/cancel", headers=auth_headers(token))
    assert cancel_response.status_code == 200

