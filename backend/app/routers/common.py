"""
公共接口 - 物品类型、地点、上传
"""
import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import settings

router = APIRouter()

def resp(data=None):
    return {"code": 0, "message": "success", "data": data}

# 物品类型 mock（与 schema 一致）
ITEM_TYPES = [
    {"id": 1, "name": "钥匙", "code": "key"},
    {"id": 2, "name": "钱包", "code": "wallet"},
    {"id": 3, "name": "杯子", "code": "cup"},
    {"id": 4, "name": "手机", "code": "phone"},
    {"id": 5, "name": "校园卡", "code": "campus_card"},
    {"id": 6, "name": "雨伞", "code": "umbrella"},
    {"id": 7, "name": "书包", "code": "bag"},
    {"id": 8, "name": "耳机", "code": "earphone"},
    {"id": 9, "name": "证件", "code": "id_card"},
    {"id": 10, "name": "其他", "code": "other"}
]

@router.get("/item-types")
def item_types():
    return resp(ITEM_TYPES)

@router.get("/locations")
def locations(keyword: str = "", campus: str = ""):
    # 简化：返回空列表，可后续接入数据库
    return resp([])

@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[-1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    # 返回完整 URL，便于小程序展示（生产环境应上传 OSS）
    url = f"{settings.base_url.rstrip('/')}/uploads/{filename}"
    return resp({"url": url})
