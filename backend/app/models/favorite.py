from sqlalchemy import BigInteger, Column, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class UserFavorite(Base):
    __tablename__ = "user_favorite"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    item_id = Column(BigInteger, ForeignKey("item.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
