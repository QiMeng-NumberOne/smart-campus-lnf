from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Item(Base):
    __tablename__ = "item"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    item_type = Column(SmallInteger, nullable=False)  # 1寻物 2招领
    item_type_id = Column(BigInteger)
    title = Column(String(128), nullable=False)
    description = Column(Text)
    status = Column(SmallInteger, default=1)  # 1待认领 2沟通中 3已归还
    location_id = Column(BigInteger)
    location_detail = Column(String(256))
    lost_found_time = Column(DateTime)
    contact_info = Column(String(256))
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    images = relationship("ItemImage", back_populates="item")

class ItemImage(Base):
    __tablename__ = "item_image"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    item_id = Column(BigInteger, ForeignKey("item.id"), nullable=False)
    image_url = Column(String(512), nullable=False)
    sort_order = Column(Integer, default=0)
    ocr_text = Column(Text)
    yolo_type_id = Column(BigInteger)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    item = relationship("Item", back_populates="images")
