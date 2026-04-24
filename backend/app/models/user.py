from sqlalchemy import Column, BigInteger, String, SmallInteger, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "user"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True)
    student_id = Column(String(32), unique=True)
    avatar = Column(String(512))
    grade = Column(String(16))
    college = Column(String(128))
    major = Column(String(128))
    role = Column(SmallInteger, default=1)
    status = Column(SmallInteger, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
