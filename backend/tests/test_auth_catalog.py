from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.main import app
from app.models import Product, UserBehavior


client = TestClient(app)


def test_register_login_and_get_me() -> None:
    username = f"test_{uuid4().hex[:10]}"
    register_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456", "phone": "13812345678"},
    )

    assert register_response.status_code == 200
    register_body = register_response.json()
    assert register_body["code"] == 0
    assert register_body["data"]["username"] == username
    assert register_body["data"]["nickname"] == username

    duplicate_response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456"},
    )
    assert duplicate_response.status_code == 400

    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "test123456"},
    )
    assert login_response.status_code == 200
    login_body = login_response.json()
    token = login_body["data"]["access_token"]
    assert login_body["data"]["token_type"] == "bearer"
    assert login_body["data"]["user"]["username"] == username

    failed_login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "wrong-password"},
    )
    assert failed_login_response.status_code == 401

    me_response = client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["data"]["username"] == username

    no_token_response = client.get("/api/users/me")
    assert no_token_response.status_code == 401


def test_catalog_endpoints_and_view_behavior() -> None:
    categories_response = client.get("/api/categories")
    assert categories_response.status_code == 200
    assert len(categories_response.json()["data"]) >= 6

    products_response = client.get("/api/products", params={"page": 1, "page_size": 5})
    assert products_response.status_code == 200
    products_data = products_response.json()["data"]
    assert products_data["total"] >= 30
    assert len(products_data["items"]) == 5

    search_response = client.get("/api/products", params={"keyword": "耳机"})
    assert search_response.status_code == 200
    assert search_response.json()["data"]["total"] >= 1

    hot_response = client.get("/api/products/hot", params={"limit": 5})
    assert hot_response.status_code == 200
    assert len(hot_response.json()["data"]) == 5

    with SessionLocal() as session:
        product = session.query(Product).filter(Product.status == "on_sale").first()
        assert product is not None
        product_id = product.id

    detail_response = client.get(f"/api/products/{product_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["data"]["id"] == product_id

    username = f"viewer_{uuid4().hex[:10]}"
    client.post("/api/auth/register", json={"username": username, "password": "test123456"})
    login_response = client.post("/api/auth/login", json={"username": username, "password": "test123456"})
    token = login_response.json()["data"]["access_token"]

    with SessionLocal() as session:
        before = (
            session.query(UserBehavior)
            .filter(UserBehavior.product_id == product_id, UserBehavior.behavior_type == "view")
            .count()
        )

    authed_detail_response = client.get(
        f"/api/products/{product_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert authed_detail_response.status_code == 200

    with SessionLocal() as session:
        after = (
            session.query(UserBehavior)
            .filter(UserBehavior.product_id == product_id, UserBehavior.behavior_type == "view")
            .count()
        )
    assert after == before + 1

