from fastapi import HTTPException
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
import bcrypt
import json
import urllib.parse
import urllib.request
from datetime import datetime

from app.core.security import create_token
from app.config import settings
from app.models.user import User
from app.models.item import Item
from app.models.favorite import UserFavorite
from app.schemas.auth import LoginRequest, RegisterRequest, UpdateProfileRequest, WechatLoginRequest

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

    def get_profile_stats(self, user_id: int) -> dict:
        lost_count = (
            self.db.query(func.count(Item.id))
            .filter(Item.user_id == user_id, Item.is_deleted == 0, Item.item_type == 1)
            .scalar()
            or 0
        )
        found_count = (
            self.db.query(func.count(Item.id))
            .filter(Item.user_id == user_id, Item.is_deleted == 0, Item.item_type == 1, Item.status == 2)
            .scalar()
            or 0
        )
        claim_count = (
            self.db.query(func.count(Item.id))
            .filter(Item.user_id == user_id, Item.is_deleted == 0, Item.item_type == 2)
            .scalar()
            or 0
        )
        likes_received = (
            self.db.query(func.count(UserFavorite.id))
            .join(Item, Item.id == UserFavorite.item_id)
            .filter(Item.user_id == user_id, Item.is_deleted == 0)
            .scalar()
            or 0
        )
        lost_ongoing_count = (
            self.db.query(func.count(Item.id))
            .filter(Item.user_id == user_id, Item.is_deleted == 0, Item.item_type == 1, Item.status == 1)
            .scalar()
            or 0
        )
        claim_ongoing_count = (
            self.db.query(func.count(Item.id))
            .filter(Item.user_id == user_id, Item.is_deleted == 0, Item.item_type == 2, Item.status == 1)
            .scalar()
            or 0
        )
        return {
            "lost_count": int(lost_count),
            "found_count": int(found_count),
            "claim_count": int(claim_count),
            "likes_received": int(likes_received),
            "lost_ongoing_count": int(lost_ongoing_count),
            "claim_ongoing_count": int(claim_ongoing_count),
        }

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
        if req.match_notification_enabled is not None:
            user.match_notification_enabled = 1 if req.match_notification_enabled else 0
            user.wechat_subscribe_at = datetime.now() if req.match_notification_enabled else None

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
            "match_notification_enabled": bool(user.match_notification_enabled),
        }

    def _fetch_openid_by_code(self, code: str) -> str:
        if not settings.wechat_appid or not settings.wechat_secret:
            raise HTTPException(status_code=503, detail="微信登录未配置，请设置 WECHAT_APPID / WECHAT_SECRET")
        q = urllib.parse.urlencode(
            {
                "appid": settings.wechat_appid,
                "secret": settings.wechat_secret,
                "js_code": code,
                "grant_type": "authorization_code",
            }
        )
        url = f"https://api.weixin.qq.com/sns/jscode2session?{q}"
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"微信登录服务异常: {exc}") from exc
        openid = data.get("openid")
        if not openid:
            msg = data.get("errmsg") or "获取openid失败"
            raise HTTPException(status_code=400, detail=f"微信登录失败: {msg}")
        return openid

    def wechat_login(self, req: WechatLoginRequest) -> dict:
        openid = self._fetch_openid_by_code(req.code)
        user = self.db.query(User).filter(User.wechat_openid == openid).first()
        nickname = (req.nickname or "").strip() or "微信用户"
        avatar = (req.avatar or "").strip() or None
        if not user:
            user = User(
                username=nickname,
                avatar=avatar,
                wechat_openid=openid,
                # 微信登录用户不依赖密码，填充随机值用于兼容现有非空约束
                password_hash=_hash_password(f"wx_{openid}"),
                match_notification_enabled=0,
                status=1,
                role=1,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # 首次授权后也允许用户更新头像昵称
            changed = False
            if req.nickname and req.nickname.strip() and req.nickname.strip() != user.username:
                user.username = req.nickname.strip()
                changed = True
            if req.avatar is not None and req.avatar != user.avatar:
                user.avatar = req.avatar
                changed = True
            if changed:
                self.db.commit()
                self.db.refresh(user)
        if user.status != 1:
            raise HTTPException(status_code=400, detail="账号已禁用")
        token = create_token(user.id)
        return {
            "user_id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "match_notification_enabled": bool(user.match_notification_enabled),
            "token": token,
        }
