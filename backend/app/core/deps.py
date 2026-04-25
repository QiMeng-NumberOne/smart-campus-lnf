from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.core.security import parse_token


def get_optional_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1)
    user_id = parse_token(token)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.status == 1).first()


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization.replace("Bearer ", "", 1)
    user_id = parse_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="登录已失效")
    user = db.query(User).filter(User.id == user_id, User.status == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    return user
