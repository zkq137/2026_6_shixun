from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_optional_current_admin, get_optional_current_user
from app.models import Admin, User
from app.schemas.ai import AiChatRequest, AiChatResponse, ConversationPublic, MessagePublic
from app.schemas.common import ApiResponse
from app.services import ai_service

router = APIRouter(prefix="/ai")


@router.post("/chat", response_model=ApiResponse[AiChatResponse])
def chat(
    payload: AiChatRequest,
    current_user: User | None = Depends(get_optional_current_user),
    current_admin: Admin | None = Depends(get_optional_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[AiChatResponse]:
    return ApiResponse(
        data=ai_service.chat(
            db,
            agent_type=payload.agent_type,
            message=payload.message,
            conversation_id=payload.conversation_id,
            user=current_user,
            admin=current_admin,
        )
    )


@router.get("/conversations", response_model=ApiResponse[list[ConversationPublic]])
def conversations(
    current_user: User | None = Depends(get_optional_current_user),
    current_admin: Admin | None = Depends(get_optional_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[list[ConversationPublic]]:
    items = ai_service.list_conversations(db, user=current_user, admin=current_admin)
    return ApiResponse(data=[ConversationPublic.model_validate(item) for item in items])


@router.get("/conversations/{conversation_id}/messages", response_model=ApiResponse[list[MessagePublic]])
def messages(
    conversation_id: int,
    current_user: User | None = Depends(get_optional_current_user),
    current_admin: Admin | None = Depends(get_optional_current_admin),
    db: Session = Depends(get_db),
) -> ApiResponse[list[MessagePublic]]:
    items = ai_service.list_messages(
        db,
        conversation_id=conversation_id,
        user=current_user,
        admin=current_admin,
    )
    return ApiResponse(data=[MessagePublic.model_validate(item) for item in items])

