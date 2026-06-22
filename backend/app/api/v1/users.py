from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models import User
from app.schemas.account import UserPublic
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/users")


@router.get("/me", response_model=ApiResponse[UserPublic])
def get_me(current_user: User = Depends(get_current_user)) -> ApiResponse[UserPublic]:
    return ApiResponse(data=UserPublic.model_validate(current_user))

