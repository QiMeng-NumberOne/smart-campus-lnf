from sqlalchemy import Column, BigInteger, String, DateTime, Integer
from sqlalchemy.sql import func

from app.database import Base


class ItemType(Base):
    __tablename__ = "item_type"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    code = Column(String(32), nullable=False)
    parent_id = Column(BigInteger, default=0)
    sort = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
