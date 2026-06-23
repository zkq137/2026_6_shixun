from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def admin_headers() -> dict[str, str]:
    response = client.post("/api/admin/auth/login", json={"username": "admin", "password": "admin123456"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def user_headers() -> dict[str, str]:
    username = f"review_user_{uuid4().hex[:10]}"
    client.post("/api/auth/register", json={"username": username, "password": "test123456"})
    response = client.post("/api/auth/login", json={"username": username, "password": "test123456"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_product_reviews_public_and_auth_required() -> None:
    public_reviews = client.get("/api/products/1/reviews")
    assert public_reviews.status_code == 200
    assert "items" in public_reviews.json()["data"]
    assert "summary" in public_reviews.json()["data"]

    unauthorized = client.post(
        "/api/products/1/reviews",
        json={"rating": 5, "content": "很好用", "is_anonymous": False},
    )
    assert unauthorized.status_code == 401


def test_create_review_validation_and_admin_status() -> None:
    headers = user_headers()

    invalid_rating = client.post(
        "/api/products/1/reviews",
        headers=headers,
        json={"rating": 6, "content": "评分非法", "is_anonymous": False},
    )
    assert invalid_rating.status_code == 422

    blank_content = client.post(
        "/api/products/1/reviews",
        headers=headers,
        json={"rating": 5, "content": "   ", "is_anonymous": False},
    )
    assert blank_content.status_code == 400

    created = client.post(
        "/api/products/1/reviews",
        headers=headers,
        json={"rating": 5, "content": "评论功能测试内容", "is_anonymous": True},
    )
    assert created.status_code == 200
    review = created.json()["data"]
    assert review["content"] == "评论功能测试内容"
    assert review["username"] == "匿名用户"
    assert review["is_purchased"] is False

    admin = admin_headers()
    admin_list = client.get("/api/admin/reviews", headers=admin, params={"status": "visible"})
    assert admin_list.status_code == 200

    hidden = client.put(f"/api/admin/reviews/{review['id']}/status", headers=admin, json={"status": "hidden"})
    assert hidden.status_code == 200
    assert hidden.json()["data"]["status"] == "hidden"

    public_reviews = client.get("/api/products/1/reviews")
    assert all(item["id"] != review["id"] for item in public_reviews.json()["data"]["items"])

    restored = client.put(f"/api/admin/reviews/{review['id']}/status", headers=admin, json={"status": "visible"})
    assert restored.status_code == 200
    assert restored.json()["data"]["status"] == "visible"


def test_review_blocks_product_delete() -> None:
    admin = admin_headers()
    category = client.post(
        "/api/admin/categories",
        headers=admin,
        json={"name": f"评论测试分类{uuid4().hex[:6]}", "sort_order": 99},
    )
    assert category.status_code == 200
    category_id = category.json()["data"]["id"]

    product = client.post(
        "/api/admin/products",
        headers=admin,
        json={
            "category_id": category_id,
            "name": f"评论保护商品{uuid4().hex[:6]}",
            "subtitle": "评论保护测试",
            "main_image": "",
            "price": "9.90",
            "stock": 10,
            "description": "已有评论时不能永久删除",
            "status": "on_sale",
        },
    )
    assert product.status_code == 200
    product_id = product.json()["data"]["id"]

    created = client.post(
        f"/api/products/{product_id}/reviews",
        headers=user_headers(),
        json={"rating": 4, "content": "这个商品已有评论", "is_anonymous": False},
    )
    assert created.status_code == 200

    deleted = client.delete(f"/api/admin/products/{product_id}", headers=admin)
    assert deleted.status_code == 409
