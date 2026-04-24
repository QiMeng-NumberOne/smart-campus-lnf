from sqlalchemy.orm import Session

from app.models.message import Message
from app.models.user import User


class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int, page: int, page_size: int):
        q = self.db.query(Message).filter(Message.to_user_id == user_id)
        total = q.count()
        rows = q.order_by(Message.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return rows, total

    def unread_count(self, user_id: int) -> int:
        return self.db.query(Message).filter(Message.to_user_id == user_id, Message.is_read == 0).count()

    def mark_read(self, user_id: int, msg_id: int) -> bool:
        row = self.db.query(Message).filter(Message.id == msg_id, Message.to_user_id == user_id).first()
        if not row:
            return False
        row.is_read = 1
        self.db.commit()
        return True

    def create(self, from_user_id: int, to_user_id: int, item_id: int, content: str) -> Message:
        row = Message(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            item_id=item_id,
            content=content,
            is_read=0,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_item_comments(self, item_id: int, limit: int = 50, order: str = "desc"):
        q = (
            self.db.query(Message, User.username)
            .join(User, User.id == Message.from_user_id)
            .filter(Message.item_id == item_id, Message.content.like("[评论%"))
        )
        if order == "asc":
            q = q.order_by(Message.created_at.asc())
        else:
            q = q.order_by(Message.created_at.desc())
        rows = q.limit(limit).all()
        return rows
