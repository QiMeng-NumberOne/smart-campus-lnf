from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_optional_user
from app.core.response import ok
from app.database import get_db
from app.models.user import User
from app.repositories.item_repository import ItemRepository
from app.schemas.recommend import RecommendEventCreate
from app.services.recommend_service import RecommendService

router = APIRouter()


@router.post("/events")
def record_event(
    body: RecommendEventCreate,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_optional_user),
):
    repo = ItemRepository(db)
    if not repo.get_item(body.item_id):
        raise HTTPException(status_code=404, detail="物品不存在")
    RecommendService(db).log_behavior(
        user.id if user else None,
        body.item_id,
        body.behavior_type.strip().lower(),
    )
    return ok()


@router.get("/related")
def related_items(
    item_id: int = Query(..., ge=1, description="当前物品ID"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    data = RecommendService(db).related_items(item_id, limit=limit)
    return ok(data)
