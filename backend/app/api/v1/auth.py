from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account import LoginResult, UserCreate, UserLogin, UserPublic
from app.schemas.common import ApiResponse
from app.services import auth_service

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=ApiResponse[UserPublic])
def register(payload: UserCreate, db: Session = Depends(get_db)) -> ApiResponse[UserPublic]:
    user = auth_service.register_user(
        db,
        username=payload.username,
        password=payload.password,
        phone=payload.phone,
    )
    return ApiResponse(data=UserPublic.model_validate(user))


@router.post("/login", response_model=ApiResponse[LoginResult])
def login(payload: UserLogin, db: Session = Depends(get_db)) -> ApiResponse[LoginResult]:
    token, user = auth_service.login_user(db, username=payload.username, password=payload.password)
    return ApiResponse(data=LoginResult(access_token=token, user=UserPublic.model_validate(user)))

