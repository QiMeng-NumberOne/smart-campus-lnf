from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, String
from sqlalchemy.sql import func

from app.database import Base


class BehaviorLog(Base):
    """用户行为日志，用于协同过滤与推荐分析。"""

    __tablename__ = "behavior_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    item_id = Column(BigInteger, ForeignKey("item.id", ondelete="CASCADE"), nullable=False, index=True)
    behavior_type = Column(String(32), nullable=False, index=True)
    extra = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
