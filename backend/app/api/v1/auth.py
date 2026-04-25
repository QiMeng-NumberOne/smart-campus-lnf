from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.response import ok
from app.schemas.auth import LoginRequest, RegisterRequest, UpdateProfileRequest, WechatLoginRequest
from app.services.auth_service import AuthService
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    data = AuthService(db).login(req)
    return ok(data)


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    data = AuthService(db).register(req)
    return ok(data)


@router.post("/wechat-login")
def wechat_login(req: WechatLoginRequest, db: Session = Depends(get_db)):
    data = AuthService(db).wechat_login(req)
    return ok(data)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return ok(
        {
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
    )


@router.get("/me/stats")
def me_stats(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = AuthService(db).get_profile_stats(user.id)
    return ok(data)


@router.put("/me")
def update_me(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = AuthService(db).update_profile(user, body)
    return ok(data)
