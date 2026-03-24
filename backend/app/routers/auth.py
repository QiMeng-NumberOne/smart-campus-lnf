"""
认证接口 - 登录/注册
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    account: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    phone: str | None = None
    student_id: str | None = None

def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=settings.jwt_expire_hours)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)

def resp(code=0, message="success", data=None):
    return {"code": code, "message": message, "data": data}

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.phone == req.account) | (User.student_id == req.account)
    ).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(status_code=400, detail="账号或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=400, detail="账号已禁用")
    token = create_token(user.id)
    return resp(data={
        "user_id": user.id,
        "username": user.username,
        "token": token,
        "expires_in": settings.jwt_expire_hours * 3600
    })

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if not req.phone and not req.student_id:
        raise HTTPException(status_code=400, detail="手机号或学号至少填一个")
    if db.query(User).filter(User.phone == req.phone).first():
        raise HTTPException(status_code=400, detail="手机号已注册")
    user = User(
        username=req.username,
        password_hash=pwd_context.hash(req.password),
        phone=req.phone,
        student_id=req.student_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_token(user.id)
    return resp(data={
        "user_id": user.id,
        "username": user.username,
        "token": token,
        "expires_in": settings.jwt_expire_hours * 3600
    })
