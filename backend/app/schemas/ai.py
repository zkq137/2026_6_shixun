from datetime import datetime

from pydantic import BaseModel, Field


class AiChatRequest(BaseModel):
    agent_type: str = Field(pattern="^(customer|recommendation|operation|inventory)$")
    conversation_id: int | None = None
    message: str = Field(min_length=1, max_length=2000)


class ToolCallPublic(BaseModel):
    tool_name: str
    status: str


class AiChatResponse(BaseModel):
    conversation_id: int
    agent_type: str
    answer: str
    tool_calls: list[ToolCallPublic]


class ConversationPublic(BaseModel):
    id: int
    user_id: int | None = None
    admin_id: int | None = None
    agent_type: str
    title: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


class MessagePublic(BaseModel):
    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AgentToolCallPublic(BaseModel):
    id: int
    conversation_id: int | None = None
    agent_type: str
    tool_name: str
    input_json: dict | None = None
    output_json: dict | None = None
    status: str
    error_message: str | None = None
    duration_ms: int | None = None
    created_at: datetime | None = None

    model_config = {"from_attributes": True}

