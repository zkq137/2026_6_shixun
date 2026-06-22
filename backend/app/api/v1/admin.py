from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models import Admin
from app.schemas.admin import AdminLogin, AdminLoginResult, AdminPublic
from app.schemas.ai import AgentToolCallPublic
from app.schemas.common import ApiResponse, PageResponse
from app.services import admin_auth_service, ai_service

router = APIRouter(prefix="/admin")


@router.post("/auth/login", response_model=ApiResponse[AdminLoginResult])
def login_admin(payload: AdminLogin, db: Session = Depends(get_db)) -> ApiResponse[AdminLoginResult]:
    token, admin = admin_auth_service.login_admin(db, username=payload.username, password=payload.password)
    return ApiResponse(data=AdminLoginResult(access_token=token, admin=AdminPublic.model_validate(admin)))


@router.get("/ai/tool-calls", response_model=ApiResponse[PageResponse[AgentToolCallPublic]])
def list_agent_tool_calls(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[PageResponse[AgentToolCallPublic]]:
    items, total = ai_service.list_tool_calls(db, page=page, page_size=page_size)
    return ApiResponse(
        data=PageResponse(
            items=[AgentToolCallPublic.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    )

