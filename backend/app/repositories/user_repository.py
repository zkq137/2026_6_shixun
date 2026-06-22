from sqlalchemy.orm import Session
from decimal import Decimal

from app.models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).one_or_none()


def create_user(
    db: Session,
    *,
    username: str,
    password_hash: str,
    phone: str | None,
) -> User:
    user = User(
        username=username,
        password_hash=password_hash,
        phone=phone,
        nickname=username,
        balance=Decimal("100000.00"),
        status="normal",
    )
    db.add(user)
    db.flush()
    return user
