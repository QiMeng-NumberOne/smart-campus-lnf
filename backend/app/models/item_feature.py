"""与库表 item_feature 一致：JSON 存向量，feature_type=0 表示 CLIP 图文一体包。"""

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, JSON, SmallInteger, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base

# feature_type: 0 = CLIP bundle，feature_vector 为 {"image":[float],"text":[float],"dim":int,"model_key":str}
FEATURE_TYPE_CLIP_BUNDLE = 0


class ItemFeature(Base):
    __tablename__ = "item_feature"
    __table_args__ = (UniqueConstraint("item_id", "feature_type", name="uk_item_feature_item_type"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(BigInteger, ForeignKey("item.id", ondelete="CASCADE"), nullable=False, index=True)
    image_id = Column(BigInteger, nullable=True)
    feature_type = Column(SmallInteger, nullable=False, default=FEATURE_TYPE_CLIP_BUNDLE)
    feature_vector = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
