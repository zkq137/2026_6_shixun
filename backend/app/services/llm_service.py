from fastapi import HTTPException, status
import httpx

from app.core.config import settings


class LlmError(RuntimeError):
    pass


def chat_completion(*, system_prompt: str, user_prompt: str) -> str:
    if not settings.llm_api_key:
        raise LlmError("LLM_API_KEY is not configured")
    if not settings.llm_base_url:
        raise LlmError("LLM_BASE_URL is not configured")

    url = settings.llm_base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": settings.llm_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }
    headers = {"Authorization": f"Bearer {settings.llm_api_key}"}

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        raise LlmError(str(exc)) from exc

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LlmError("Invalid LLM response") from exc


def raise_llm_http_error(error: Exception):
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"code": 600, "message": f"LLM service unavailable: {error}"},
    )

