from sqlalchemy import Column, BigInteger, String, Integer, DateTime, JSON, Text
from sqlalchemy.sql import func

from app.database import Base


class RecognitionLog(Base):
    __tablename__ = "recognition_log"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(BigInteger)
    image_id = Column(BigInteger)
    model_type = Column(String(32), nullable=False)
    model_version = Column(String(64))
    status = Column(String(16), default="success")
    input_info = Column(JSON)
    output_info = Column(JSON)
    error = Column(Text)
    cost_ms = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
