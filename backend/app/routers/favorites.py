"""
收藏接口 - 简化实现
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db

router = APIRouter()

def resp(data=None):
    return {"code": 0, "message": "success", "data": data}

class FavoriteCreate(BaseModel):
    item_id: int

@router.post("")
def add_favorite(body: FavoriteCreate, db: Session = Depends(get_db)):
    # 简化：暂不落库
    return resp()

@router.delete("/{item_id}")
def remove_favorite(item_id: int, db: Session = Depends(get_db)):
    return resp()

@router.get("")
def list_favorites(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    # 简化：返回空列表
    return resp({"list": [], "total": 0, "page": page, "page_size": page_size})
