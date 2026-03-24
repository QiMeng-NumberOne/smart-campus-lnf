"""
AI 接口 - 图片识别 (YOLO + OCR)
"""
from fastapi import APIRouter, UploadFile, File

router = APIRouter()

def resp(data=None):
    return {"code": 0, "message": "success", "data": data}

@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    # 简化：返回 mock，后续接入 YOLO、OCR 模型
    content = await file.read()
    if len(content) == 0:
        return {"code": 40001, "message": "图片无效", "data": None}
    return resp({
        "yolo": {"item_type_id": 1, "item_type_name": "钥匙", "bbox": [0, 0, 100, 100]},
        "ocr": {"text": ""}
    })
