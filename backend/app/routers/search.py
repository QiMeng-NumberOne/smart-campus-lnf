"""
搜索接口 - 以图搜图、以文搜文
"""
from fastapi import APIRouter, Depends, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.item import Item, ItemImage

router = APIRouter()

def resp(data=None):
    return {"code": 0, "message": "success", "data": data}

@router.post("/by-image")
async def search_by_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 简化：接收图片后返回 mock 列表，后续接入 YOLO+OCR+CLIP
    content = await file.read()
    if len(content) == 0:
        return {"code": 40001, "message": "图片无效", "data": None}
    items = db.query(Item).filter(Item.status == 1).order_by(Item.created_at.desc()).limit(20).all()
    list_data = []
    for it in items:
        imgs = db.query(ItemImage).filter(ItemImage.item_id == it.id).limit(1).all()
        list_data.append({
            "id": it.id, "item_type": it.item_type, "item_type_name": "其他",
            "title": it.title,
            "cover_image": imgs[0].image_url if imgs else "",
            "similarity": 0.9, "location_name": it.location_detail or "",
            "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
            "status": it.status
        })
    return resp({"list": list_data})

@router.get("/by-text")
def search_by_text(
    keyword: str = Query(...),
    item_type: Optional[int] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    q = db.query(Item).filter(Item.status == 1)
    if item_type:
        q = q.filter(Item.item_type == item_type)
    if keyword:
        from sqlalchemy import or_
        q = q.filter(or_(
            Item.title.contains(keyword),
            (Item.description != None) & Item.description.contains(keyword)
        ))
    total = q.count()
    items = q.order_by(Item.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    list_data = []
    for it in items:
        imgs = db.query(ItemImage).filter(ItemImage.item_id == it.id).limit(1).all()
        list_data.append({
            "id": it.id, "item_type": it.item_type, "item_type_name": "其他",
            "title": it.title,
            "cover_image": imgs[0].image_url if imgs else "",
            "location_name": it.location_detail or "",
            "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
            "status": it.status
        })
    return resp({"list": list_data, "total": total, "page": page, "page_size": page_size})
