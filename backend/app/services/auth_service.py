from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories import user_repository


def register_user(db: Session, *, username: str, password: str, phone: str | None) -> User:
    existing = user_repository.get_user_by_username(db, username)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")
    user = user_repository.create_user(
        db,
        username=username,
        password_hash=hash_password(password),
        phone=phone,
    )
    db.commit()
    db.refresh(user)
    return user


def login_user(db: Session, *, username: str, password: str) -> tuple[str, User]:
    user = user_repository.get_user_by_username(db, username)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    if user.status == "disabled":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is disabled")
    token = create_access_token(str(user.id), {"type": "user"})
    return token, user

