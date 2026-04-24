from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Text, SmallInteger
from sqlalchemy.sql import func

from app.database import Base


class Message(Base):
    __tablename__ = "message"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    from_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    to_user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("item.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(SmallInteger, nullable=False, default=0)
    created_at = Column(DateTime, server_default=func.now())
