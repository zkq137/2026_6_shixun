from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Admin, AgentToolCall, AiConversation, AiMessage, User
from app.schemas.ai import AiChatResponse, ToolCallPublic
from app.services import llm_service
from app.tools.registry import registry


USER_AGENTS = {"customer", "recommendation"}
ADMIN_AGENTS = {"operation", "inventory"}


def _conversation_owner_filter(db: Session, conversation_id: int, user: User | None, admin: Admin | None):
    conversation = db.get(AiConversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
    if user and conversation.user_id == user.id:
        return conversation
    if admin and conversation.admin_id == admin.id:
        return conversation
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")


def _get_or_create_conversation(
    db: Session,
    *,
    agent_type: str,
    message: str,
    conversation_id: int | None,
    user: User | None,
    admin: Admin | None,
) -> AiConversation:
    if conversation_id:
        conversation = _conversation_owner_filter(db, conversation_id, user, admin)
        if conversation.agent_type != agent_type:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent type mismatch")
        return conversation

    conversation = AiConversation(
        user_id=user.id if user else None,
        admin_id=admin.id if admin else None,
        agent_type=agent_type,
        title=message[:50],
    )
    db.add(conversation)
    db.flush()
    return conversation


def _call_tool(
    db: Session,
    *,
    conversation_id: int,
    agent_type: str,
    tool_name: str,
    payload: dict[str, Any],
    tool_calls: list[ToolCallPublic],
    tool_results: dict[str, Any],
) -> dict[str, Any]:
    result = registry.call(
        db,
        conversation_id=conversation_id,
        agent_type=agent_type,
        tool_name=tool_name,
        payload=payload,
    )
    status_text = "failed" if "error" in result else "success"
    tool_calls.append(ToolCallPublic(tool_name=tool_name, status=status_text))
    tool_results[tool_name] = result
    return result


def _run_customer_agent(db: Session, conversation_id: int, message: str, user: User):
    tool_calls: list[ToolCallPublic] = []
    tool_results: dict[str, Any] = {}
    _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="customer",
        tool_name="query_faq",
        payload={"question": message},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    if "订单" in message or "order" in message.lower():
        _call_tool(
            db,
            conversation_id=conversation_id,
            agent_type="customer",
            tool_name="get_user_orders",
            payload={"user_id": user.id, "limit": 5},
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    if "商品" in message or "推荐" in message:
        _call_tool(
            db,
            conversation_id=conversation_id,
            agent_type="customer",
            tool_name="search_products",
            payload={"keyword": message[:20], "limit": 5},
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    return tool_calls, tool_results


def _run_recommendation_agent(db: Session, conversation_id: int, message: str, user: User):
    tool_calls: list[ToolCallPublic] = []
    tool_results: dict[str, Any] = {}
    behavior = _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="recommendation",
        tool_name="get_user_behavior",
        payload={"user_id": user.id, "limit": 20},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    first_product_id = None
    for item in behavior.get("items", []):
        if item.get("product_id"):
            first_product_id = item["product_id"]
            break
    if first_product_id:
        _call_tool(
            db,
            conversation_id=conversation_id,
            agent_type="recommendation",
            tool_name="get_similar_products",
            payload={"product_id": first_product_id, "limit": 8},
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="recommendation",
        tool_name="get_hot_products",
        payload={"limit": 8},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    return tool_calls, tool_results


def _run_operation_agent(db: Session, conversation_id: int, message: str):
    tool_calls: list[ToolCallPublic] = []
    tool_results: dict[str, Any] = {}
    _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="operation",
        tool_name="get_sales_statistics",
        payload={"days": 7},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="operation",
        tool_name="get_user_behavior",
        payload={"limit": 20},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    return tool_calls, tool_results


def _run_inventory_agent(db: Session, conversation_id: int, message: str):
    tool_calls: list[ToolCallPublic] = []
    tool_results: dict[str, Any] = {}
    sales = _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="inventory",
        tool_name="get_sales_statistics",
        payload={"days": 7},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    product_id = None
    for item in sales.get("top_products", []):
        product_id = item.get("product_id")
        if product_id:
            break
    if product_id is None:
        product_id = 1
    prediction = _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="inventory",
        tool_name="predict_product_sales",
        payload={"product_id": product_id, "days": 7},
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    risk = _call_tool(
        db,
        conversation_id=conversation_id,
        agent_type="inventory",
        tool_name="check_inventory_risk",
        payload={
            "product_id": product_id,
            "predicted_sales": prediction.get("predicted_count", 0),
        },
        tool_calls=tool_calls,
        tool_results=tool_results,
    )
    if risk.get("found") and risk.get("risk_level") in {"medium", "high"}:
        _call_tool(
            db,
            conversation_id=conversation_id,
            agent_type="inventory",
            tool_name="create_inventory_alert",
            payload=risk,
            tool_calls=tool_calls,
            tool_results=tool_results,
        )
    return tool_calls, tool_results


def _system_prompt(agent_type: str) -> str:
    prompts = {
        "customer": "You are a customer service agent for an AI mall. Answer politely using only tool facts.",
        "recommendation": "You are a product recommendation agent. Recommend products and explain why.",
        "operation": "You are an operations analysis agent. Provide conclusions, evidence, and actions.",
        "inventory": "You are an inventory agent. Explain sales forecast, stock risk, and replenishment actions.",
    }
    return prompts[agent_type]


def _build_user_prompt(message: str, tool_results: dict[str, Any]) -> str:
    return (
        "User message:\n"
        f"{message}\n\n"
        "Tool results as JSON:\n"
        f"{json.dumps(tool_results, ensure_ascii=False, default=str)}\n\n"
        "Please answer in Chinese. Keep it concise and actionable."
    )


def chat(
    db: Session,
    *,
    agent_type: str,
    message: str,
    conversation_id: int | None,
    user: User | None,
    admin: Admin | None,
) -> AiChatResponse:
    if agent_type in USER_AGENTS and user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User authentication required")
    if agent_type in ADMIN_AGENTS and admin is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin authentication required")

    conversation = _get_or_create_conversation(
        db,
        agent_type=agent_type,
        message=message,
        conversation_id=conversation_id,
        user=user,
        admin=admin,
    )
    db.add(AiMessage(conversation_id=conversation.id, role="user", content=message))
    db.flush()

    if agent_type == "customer":
        tool_calls, tool_results = _run_customer_agent(db, conversation.id, message, user)
    elif agent_type == "recommendation":
        tool_calls, tool_results = _run_recommendation_agent(db, conversation.id, message, user)
    elif agent_type == "operation":
        tool_calls, tool_results = _run_operation_agent(db, conversation.id, message)
    else:
        tool_calls, tool_results = _run_inventory_agent(db, conversation.id, message)

    try:
        answer = llm_service.chat_completion(
            system_prompt=_system_prompt(agent_type),
            user_prompt=_build_user_prompt(message, tool_results),
        )
    except llm_service.LlmError as exc:
        db.rollback()
        llm_service.raise_llm_http_error(exc)

    db.add(AiMessage(conversation_id=conversation.id, role="assistant", content=answer))
    db.commit()
    return AiChatResponse(
        conversation_id=conversation.id,
        agent_type=agent_type,
        answer=answer,
        tool_calls=tool_calls,
    )


def list_conversations(db: Session, *, user: User | None, admin: Admin | None) -> list[AiConversation]:
    query = db.query(AiConversation)
    if user:
        query = query.filter(AiConversation.user_id == user.id)
    elif admin:
        query = query.filter(AiConversation.admin_id == admin.id)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return query.order_by(AiConversation.updated_at.desc(), AiConversation.id.desc()).all()


def list_messages(
    db: Session,
    *,
    conversation_id: int,
    user: User | None,
    admin: Admin | None,
) -> list[AiMessage]:
    _conversation_owner_filter(db, conversation_id, user, admin)
    return (
        db.query(AiMessage)
        .filter(AiMessage.conversation_id == conversation_id)
        .order_by(AiMessage.id.asc())
        .all()
    )


def list_tool_calls(db: Session, *, page: int, page_size: int) -> tuple[list[AgentToolCall], int]:
    query = db.query(AgentToolCall)
    total = query.count()
    items = (
        query.order_by(AgentToolCall.created_at.desc(), AgentToolCall.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return items, total

