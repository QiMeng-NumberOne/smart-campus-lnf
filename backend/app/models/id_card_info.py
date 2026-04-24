from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class IdCardInfo(Base):
    __tablename__ = "id_card_info"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(BigInteger, ForeignKey("item.id"), nullable=False, unique=True)
    name_plain = Column(String(64), nullable=False)
    id_no_enc = Column(String(1024))
    id_no_last4 = Column(String(8))
    address_enc = Column(String(2048))
    source = Column(String(16), default="manual")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
