from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import json

from app.core.deps import get_current_user, get_optional_user
from app.core.response import ok
from app.database import get_db
from app.models.user import User
from app.repositories.item_repository import ItemRepository
from app.repositories.message_repository import MessageRepository
from app.schemas.comment import CommentCreate
from app.schemas.item import ItemCreate, ItemStatusUpdate
from app.services.item_service import ItemService
from app.services.match_notify_service import MatchNotifyService
from app.services.recommend_service import RecommendService

router = APIRouter()


def _encode_comment_payload(content: str, reply_to_comment_id: int | None = None, reply_to_username: str | None = None) -> str:
    payload = {
        "text": content.strip(),
        "reply_to_comment_id": reply_to_comment_id,
        "reply_to_username": reply_to_username,
    }
    return "[评论JSON]" + json.dumps(payload, ensure_ascii=False)


def _decode_comment_payload(raw: str) -> dict:
    if raw.startswith("[评论JSON]"):
        body = raw.replace("[评论JSON]", "", 1)
        try:
            data = json.loads(body)
            return {
                "text": data.get("text", ""),
                "reply_to_comment_id": data.get("reply_to_comment_id"),
                "reply_to_username": data.get("reply_to_username"),
            }
        except Exception:
            return {"text": body, "reply_to_comment_id": None, "reply_to_username": None}
    return {"text": raw.replace("[评论]", "", 1), "reply_to_comment_id": None, "reply_to_username": None}


@router.get("")
def list_items(
    item_type: int | None = None,
    item_type_id: int | None = None,
    status: int = 1,
    keyword: str | None = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    service = ItemService(ItemRepository(db))
    return ok(service.list_items(item_type, status, page, page_size, keyword=keyword, item_type_id=item_type_id))


@router.get("/mine")
def mine(
    page: int = 1,
    page_size: int = 10,
    item_type: int | None = None,
    status: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ItemService(ItemRepository(db))
    return ok(service.my_items(user.id, page, page_size, item_type=item_type, status=status))


@router.get("/{item_id}/recommendations")
def item_recommendations(
    item_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """相关推荐（与 /api/v1/recommend/related 等价，挂在物品路由下便于部署与缓存）。"""
    return ok(RecommendService(db).related_items(item_id, limit=limit))


@router.get("/{item_id}")
def detail(
    item_id: int,
    db: Session = Depends(get_db),
    viewer: User | None = Depends(get_optional_user),
):
    service = ItemService(ItemRepository(db))
    data = service.get_item_detail(item_id)
    if not data:
        raise HTTPException(status_code=404, detail="物品不存在")
    try:
        RecommendService(db).log_behavior(viewer.id if viewer else None, item_id, "view")
    except Exception:
        pass
    return ok(data)


@router.post("")
def create(
    body: ItemCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ItemService(ItemRepository(db))
    return ok(service.create_item(user.id, body))


@router.put("/{item_id}/status")
def update_status(
    item_id: int,
    body: ItemStatusUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = ItemService(ItemRepository(db))
    data, err = service.update_status(user.id, item_id, body.status)
    if err:
        raise HTTPException(status_code=400, detail=err)
    return ok(data)


@router.post("/{item_id}/match-notify")
def trigger_match_notify(
    item_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = ItemRepository(db).get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    if item.user_id != user.id:
        raise HTTPException(status_code=403, detail="仅发布者可触发匹配")
    count = MatchNotifyService(db).notify_for_new_item(item_id)
    return ok({"match_notify_count": count})


@router.get("/{item_id}/comments")
def list_comments(item_id: int, order: str = "desc", db: Session = Depends(get_db)):
    item_repo = ItemRepository(db)
    item = item_repo.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    rows = MessageRepository(db).list_item_comments(item_id, order=order)
    data = [
        (
            lambda parsed: {
                "id": msg.id,
                "from_user_id": msg.from_user_id,
                "from_username": username,
                "content": parsed["text"],
                "reply_to_comment_id": parsed["reply_to_comment_id"],
                "reply_to_username": parsed["reply_to_username"],
                "created_at": str(msg.created_at),
            }
        )(_decode_comment_payload(msg.content))
        for msg, username in rows
    ]
    return ok({"list": data})


@router.post("/{item_id}/comments")
def create_comment(
    item_id: int,
    body: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item_repo = ItemRepository(db)
    item = item_repo.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="物品不存在")
    content = _encode_comment_payload(
        content=body.content,
        reply_to_comment_id=body.reply_to_comment_id,
        reply_to_username=body.reply_to_username,
    )
    msg = MessageRepository(db).create(
        from_user_id=user.id,
        to_user_id=item.user_id,
        item_id=item_id,
        content=content,
    )
    try:
        RecommendService(db).log_behavior(user.id, item_id, "comment")
    except Exception:
        pass
    return ok({"id": msg.id})
