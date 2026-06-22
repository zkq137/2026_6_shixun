from sqlalchemy.orm import Session

from app.models import Admin


def get_admin_by_username(db: Session, username: str) -> Admin | None:
    return db.query(Admin).filter(Admin.username == username).one_or_none()

