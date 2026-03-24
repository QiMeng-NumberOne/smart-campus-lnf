"""
物品接口 - CRUD、推荐
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.item import Item, ItemImage

router = APIRouter()

# 简化：暂不做 JWT 校验，后续可加 Depends(get_current_user)
def resp(data=None):
    return {"code": 0, "message": "success", "data": data}

class ItemCreate(BaseModel):
    item_type: int
    title: str
    description: Optional[str] = None
    location_id: Optional[int] = None
    location_detail: Optional[str] = None
    lost_found_time: Optional[str] = None
    contact_info: Optional[str] = None
    images: list[dict]

@router.get("")
def list_items(
    item_type: Optional[int] = None,
    status: Optional[int] = 1,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    q = db.query(Item).filter(Item.status == status)
    if item_type:
        q = q.filter(Item.item_type == item_type)
    total = q.count()
    items = q.order_by(Item.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    list_data = []
    for it in items:
        imgs = db.query(ItemImage).filter(ItemImage.item_id == it.id).order_by(ItemImage.sort_order).all()
        list_data.append({
            "id": it.id,
            "item_type": it.item_type,
            "item_type_name": "其他",
            "title": it.title,
            "cover_image": imgs[0].image_url if imgs else "",
            "location_name": it.location_detail or "",
            "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
            "status": it.status,
            "created_at": str(it.created_at)
        })
    return resp({"list": list_data, "total": total, "page": page, "page_size": page_size})

@router.get("/{item_id}")
def get_item(item_id: int, db: Session = Depends(get_db)):
    it = db.query(Item).filter(Item.id == item_id).first()
    if not it:
        return {"code": 40400, "message": "不存在", "data": None}
    imgs = db.query(ItemImage).filter(ItemImage.item_id == it.id).order_by(ItemImage.sort_order).all()
    return resp({
        "id": it.id,
        "user_id": it.user_id,
        "username": "用户",
        "avatar": None,
        "item_type": it.item_type,
        "item_type_name": "其他",
        "title": it.title,
        "description": it.description,
        "status": it.status,
        "location": {"id": it.location_id, "name": it.location_detail, "longitude": None, "latitude": None},
        "location_detail": it.location_detail,
        "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
        "contact_info": it.contact_info,
        "view_count": it.view_count,
        "images": [{"id": i.id, "url": i.image_url} for i in imgs],
        "is_favorited": False,
        "created_at": str(it.created_at)
    })

@router.post("")
def create_item(body: ItemCreate, db: Session = Depends(get_db)):
    # 简化：user_id 暂用 1
    item = Item(
        user_id=1,
        item_type=body.item_type,
        title=body.title,
        description=body.description,
        location_id=body.location_id,
        location_detail=body.location_detail,
        contact_info=body.contact_info,
        images=[]
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    for i, img in enumerate(body.images):
        im = ItemImage(item_id=item.id, image_url=img.get("url", ""), sort_order=i)
        db.add(im)
    db.commit()
    return resp({"id": item.id, "item_type": item.item_type, "title": item.title, "status": 1, "created_at": str(item.created_at)})

@router.get("/{item_id}/recommendations")
def recommendations(item_id: int, top_n: int = 10, db: Session = Depends(get_db)):
    # 简化：返回同类型最近几条
    it = db.query(Item).filter(Item.id == item_id).first()
    if not it:
        return resp({"list": []})
    items = db.query(Item).filter(Item.id != item_id, Item.status == 1).order_by(Item.created_at.desc()).limit(top_n).all()
    list_data = []
    for i in items:
        imgs = db.query(ItemImage).filter(ItemImage.item_id == i.id).limit(1).all()
        list_data.append({
            "id": i.id, "item_type": i.item_type, "title": i.title,
            "cover_image": imgs[0].image_url if imgs else "",
            "similarity": 0.85, "location_name": i.location_detail or "",
            "status": i.status
        })
    return resp({"list": list_data})
