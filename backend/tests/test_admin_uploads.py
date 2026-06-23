from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

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
    username = f"upload_guard_{uuid4().hex[:10]}"
    client.post("/api/auth/register", json={"username": username, "password": "test123456"})
    response = client.post("/api/auth/login", json={"username": username, "password": "test123456"})
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_upload_product_image_success() -> None:
    response = client.post(
        "/api/admin/uploads/product-image",
        headers=admin_headers(),
        files={"file": ("product.jpg", b"\xff\xd8\xff\xe0fake-jpeg", "image/jpeg")},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["url"].startswith("/uploads/products/")
    assert data["filename"].endswith(".jpg")
    assert data["size"] > 0
    assert data["content_type"] == "image/jpeg"

    static_response = client.get(data["url"])
    assert static_response.status_code == 200

    uploaded = Path("uploads/products") / data["filename"]
    if uploaded.exists():
        uploaded.unlink()


def test_upload_product_image_requires_admin() -> None:
    missing = client.post(
        "/api/admin/uploads/product-image",
        files={"file": ("product.jpg", b"fake", "image/jpeg")},
    )
    assert missing.status_code == 401

    forbidden = client.post(
        "/api/admin/uploads/product-image",
        headers=user_headers(),
        files={"file": ("product.jpg", b"fake", "image/jpeg")},
    )
    assert forbidden.status_code == 401


def test_upload_product_image_rejects_invalid_type_and_large_file() -> None:
    headers = admin_headers()
    invalid = client.post(
        "/api/admin/uploads/product-image",
        headers=headers,
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert invalid.status_code == 400

    large = client.post(
        "/api/admin/uploads/product-image",
        headers=headers,
        files={"file": ("large.png", b"0" * (5 * 1024 * 1024 + 1), "image/png")},
    )
    assert large.status_code == 400
