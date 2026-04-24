import os
import uuid

import aiofiles
from fastapi import APIRouter, UploadFile, File

from app.config import settings
from app.core.response import ok

router = APIRouter()

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
    {"id": 10, "name": "其他", "code": "other"},
]


@router.get("/item-types")
def item_types():
    return ok(ITEM_TYPES)


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    os.makedirs(settings.upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[-1] or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(settings.upload_dir, filename)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())
    url = f"{settings.base_url.rstrip('/')}/uploads/{filename}"
    return ok({"url": url})
