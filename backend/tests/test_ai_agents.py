from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services import llm_service


client = TestClient(app)


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def register_user(prefix: str = "agent") -> str:
    username = f"{prefix}_{uuid4().hex[:10]}"
    response = client.post(
        "/api/auth/register",
        json={"username": username, "password": "test123456"},
    )
    assert response.status_code == 200
    login_response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "test123456"},
    )
    assert login_response.status_code == 200
    return login_response.json()["data"]["access_token"]


def login_admin() -> str:
    response = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "admin123456"},
    )
    assert response.status_code == 200
    return response.json()["data"]["access_token"]


def fake_llm(system_prompt: str, user_prompt: str) -> str:
    return f"模拟LLM回答：{system_prompt[:16]}"


def test_admin_login_success_and_failure() -> None:
    token = login_admin()
    assert token

    failed = client.post(
        "/api/admin/auth/login",
        json={"username": "admin", "password": "wrong-password"},
    )
    assert failed.status_code == 401


def test_customer_agent_writes_conversation_messages_and_tool_log(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "chat_completion", fake_llm)
    token = register_user("customer")

    response = client.post(
        "/api/ai/chat",
        headers=auth_headers(token),
        json={"agent_type": "customer", "message": "怎么退货？我的订单在哪里看？"},
    )

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["agent_type"] == "customer"
    assert data["answer"].startswith("模拟LLM回答")
    tool_names = {item["tool_name"] for item in data["tool_calls"]}
    assert "query_faq" in tool_names
    assert "get_user_orders" in tool_names

    messages = client.get(
        f"/api/ai/conversations/{data['conversation_id']}/messages",
        headers=auth_headers(token),
    )
    assert messages.status_code == 200
    assert len(messages.json()["data"]) == 2


def test_recommendation_agent_calls_behavior_and_product_tools(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "chat_completion", fake_llm)
    token = register_user("recommend")

    response = client.post(
        "/api/ai/chat",
        headers=auth_headers(token),
        json={"agent_type": "recommendation", "message": "给我推荐一些商品"},
    )

    assert response.status_code == 200
    tool_names = {item["tool_name"] for item in response.json()["data"]["tool_calls"]}
    assert "get_user_behavior" in tool_names
    assert "get_hot_products" in tool_names


def test_operation_and_inventory_agents_require_admin_and_call_tools(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "chat_completion", fake_llm)
    user_token = register_user("normal")
    admin_token = login_admin()

    forbidden = client.post(
        "/api/ai/chat",
        headers=auth_headers(user_token),
        json={"agent_type": "operation", "message": "最近7天哪些商品销量最好？"},
    )
    assert forbidden.status_code == 403

    operation = client.post(
        "/api/ai/chat",
        headers=auth_headers(admin_token),
        json={"agent_type": "operation", "message": "最近7天哪些商品销量最好？"},
    )
    assert operation.status_code == 200
    op_tools = {item["tool_name"] for item in operation.json()["data"]["tool_calls"]}
    assert "get_sales_statistics" in op_tools
    assert "get_user_behavior" in op_tools

    inventory = client.post(
        "/api/ai/chat",
        headers=auth_headers(admin_token),
        json={"agent_type": "inventory", "message": "帮我看看库存风险"},
    )
    assert inventory.status_code == 200
    inv_tools = {item["tool_name"] for item in inventory.json()["data"]["tool_calls"]}
    assert "predict_product_sales" in inv_tools
    assert "check_inventory_risk" in inv_tools


def test_ai_auth_and_admin_tool_call_log(monkeypatch) -> None:
    monkeypatch.setattr(llm_service, "chat_completion", fake_llm)

    unauthorized = client.post(
        "/api/ai/chat",
        json={"agent_type": "customer", "message": "怎么退货？"},
    )
    assert unauthorized.status_code == 401

    user_token = register_user("log")
    client.post(
        "/api/ai/chat",
        headers=auth_headers(user_token),
        json={"agent_type": "customer", "message": "怎么退货？"},
    )

    no_admin = client.get("/api/admin/ai/tool-calls", headers=auth_headers(user_token))
    assert no_admin.status_code == 401

    admin_token = login_admin()
    log_response = client.get("/api/admin/ai/tool-calls", headers=auth_headers(admin_token))
    assert log_response.status_code == 200
    assert log_response.json()["data"]["total"] >= 1


def test_llm_failure_returns_600(monkeypatch) -> None:
    def fail_llm(system_prompt: str, user_prompt: str) -> str:
        raise llm_service.LlmError("boom")

    monkeypatch.setattr(llm_service, "chat_completion", fail_llm)
    token = register_user("fail")

    response = client.post(
        "/api/ai/chat",
        headers=auth_headers(token),
        json={"agent_type": "customer", "message": "怎么退货？"},
    )

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == 600

