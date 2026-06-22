from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models import Admin
from app.repositories import admin_repository


def login_admin(db: Session, *, username: str, password: str) -> tuple[str, Admin]:
    admin = admin_repository.get_admin_by_username(db, username)
    if not admin or not verify_password(password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if admin.status == "disabled":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin is disabled")
    token = create_access_token(str(admin.id), {"type": "admin"})
    return token, admin

