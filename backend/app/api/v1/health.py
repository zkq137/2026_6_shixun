from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/health", response_model=ApiResponse[dict])
def health_check() -> ApiResponse[dict]:
    return ApiResponse(data={"status": "ok"})


@router.get("/health/db", response_model=ApiResponse[dict])
def database_health_check() -> ApiResponse[dict]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return ApiResponse(data={"status": "ok"})
    except SQLAlchemyError as exc:
        return ApiResponse(code=500, message="database unavailable", data={"error": str(exc)})

