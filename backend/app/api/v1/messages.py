from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.response import ok
from app.database import get_db
from app.models.user import User
from app.repositories.message_repository import MessageRepository
from app.services.message_service import MessageService

router = APIRouter()


@router.get("")
def list_messages(
    page: int = 1,
    page_size: int = 10,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = MessageService(MessageRepository(db)).list_messages(user.id, page, page_size)
    return ok(data)


@router.get("/unread-count")
def unread_count(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = MessageService(MessageRepository(db)).unread_count(user.id)
    return ok(data)


@router.post("/{message_id}/read")
def mark_read(message_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    success = MessageService(MessageRepository(db)).mark_read(user.id, message_id)
    if not success:
        raise HTTPException(status_code=404, detail="消息不存在")
    return ok()
