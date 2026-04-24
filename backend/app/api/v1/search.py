import io
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session
from PIL import Image

from app.core.response import ok
from app.database import get_db
from app.models.item_feature import FEATURE_TYPE_CLIP_BUNDLE, ItemFeature
from app.services.clip_service import ClipService

router = APIRouter()


@router.get("/health")
def health(db: Session = Depends(get_db)):
    info = ClipService.runtime_info()
    try:
        info["indexed_items"] = (
            db.query(ItemFeature).filter(ItemFeature.feature_type == FEATURE_TYPE_CLIP_BUNDLE).count()
        )
    except Exception:
        info["indexed_items"] = -1
    return ok(info)


@router.post("/by-image")
async def by_image(
    file: UploadFile = File(...),
    item_type: Optional[int] = Form(default=None),
    item_type_id: Optional[int] = Form(default=None),
    top_k: int = Form(default=20),
    db: Session = Depends(get_db),
):
    load_err = ClipService.load_error()
    if load_err:
        raise HTTPException(status_code=503, detail=f"CLIP模型不可用: {load_err}")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="图片无效")
    try:
        image = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="图片格式不支持")
    service = ClipService(db)
    limit = min(max(top_k, 1), 50)
    rows, note = service.search_by_image(image=image, item_type=item_type, item_type_id=item_type_id, top_k=limit)
    return ok({"list": rows, "note": note or ""})


@router.get("/by-text")
def by_text(
    keyword: str = Query(..., min_length=1),
    item_type: Optional[int] = None,
    item_type_id: Optional[int] = None,
    top_k: int = 20,
    db: Session = Depends(get_db),
):
    load_err = ClipService.load_error()
    if load_err:
        raise HTTPException(status_code=503, detail=f"CLIP模型不可用: {load_err}")
    service = ClipService(db)
    limit = min(max(top_k, 1), 50)
    rows, note = service.search_by_text(keyword=keyword.strip(), item_type=item_type, item_type_id=item_type_id, top_k=limit)
    return ok({"list": rows, "note": note or ""})
