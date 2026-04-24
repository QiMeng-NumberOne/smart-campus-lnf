from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_
import bcrypt

from app.core.security import create_token
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, UpdateProfileRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, password_hash: str) -> bool:
    # 先尝试 passlib，若环境组合触发 bcrypt 72-byte 异常则回退到原生 bcrypt
    try:
        return pwd_context.verify(password, password_hash)
    except Exception:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception:
            return False


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def login(self, req: LoginRequest) -> dict:
        user = self.db.query(User).filter(or_(User.phone == req.account, User.student_id == req.account)).first()
        if not user:
            raise HTTPException(status_code=400, detail="账号或密码错误")
        try:
            password_ok = _verify_password(req.password, user.password_hash)
        except Exception:
            password_ok = False
        if not password_ok:
            raise HTTPException(status_code=400, detail="账号或密码错误")
        if user.status != 1:
            raise HTTPException(status_code=400, detail="账号已禁用")
        token = create_token(user.id)
        return {"user_id": user.id, "username": user.username, "token": token}

    def register(self, req: RegisterRequest) -> dict:
        if not req.phone and not req.student_id:
            raise HTTPException(status_code=400, detail="手机号或学号至少填一个")
        if req.phone and self.db.query(User).filter(User.phone == req.phone).first():
            raise HTTPException(status_code=400, detail="手机号已注册")
        if req.student_id and self.db.query(User).filter(User.student_id == req.student_id).first():
            raise HTTPException(status_code=400, detail="学号已注册")
        user = User(
            username=req.username,
            password_hash=_hash_password(req.password),
            phone=req.phone,
            student_id=req.student_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        token = create_token(user.id)
        return {"user_id": user.id, "username": user.username, "token": token}

    def update_profile(self, user: User, req: UpdateProfileRequest) -> dict:
        if req.phone and req.phone != user.phone:
            exists = self.db.query(User).filter(User.phone == req.phone, User.id != user.id).first()
            if exists:
                raise HTTPException(status_code=400, detail="手机号已被占用")
            user.phone = req.phone
        if req.student_id and req.student_id != user.student_id:
            exists = self.db.query(User).filter(User.student_id == req.student_id, User.id != user.id).first()
            if exists:
                raise HTTPException(status_code=400, detail="学号已被占用")
            user.student_id = req.student_id
        if req.username is not None:
            user.username = req.username.strip() or user.username
        if req.avatar is not None:
            user.avatar = req.avatar
        if req.grade is not None:
            user.grade = req.grade
        if req.college is not None:
            user.college = req.college
        if req.major is not None:
            user.major = req.major

        self.db.commit()
        self.db.refresh(user)
        return {
            "id": user.id,
            "username": user.username,
            "phone": user.phone,
            "student_id": user.student_id,
            "avatar": user.avatar,
            "grade": user.grade,
            "college": user.college,
            "major": user.major,
        }
