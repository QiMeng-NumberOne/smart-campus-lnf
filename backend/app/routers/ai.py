"""
AI 接口 - 图片识别 (YOLO)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from ultralytics import YOLO
from PIL import Image
import io
import os

router = APIRouter()

# 加载 YOLO 模型
try:
    model_path = os.path.join(os.path.dirname(__file__), "../../yolo_model/yolo26n.pt")
    model = YOLO(model_path)
    print(f"Model loaded successfully from: {model_path}")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# 类别映射
class_map = {
    'keys': '钥匙',
    'id_card': '身份证/校园卡',
    'glasses': '眼镜'
}

def resp(data=None):
    return {"code": 200, "message": "success", "data": data}

@router.post("/recognize")
async def recognize(file: UploadFile = File(...)):
    try:
        # 检查模型是否加载成功
        if model is None:
            raise HTTPException(status_code=500, detail="模型加载失败")
        
        # 读取图片
        content = await file.read()
        if len(content) == 0:
            return {"code": 400, "message": "图片无效", "data": None}
        
        # 转换为 PIL 格式
        img = Image.open(io.BytesIO(content))
        
        # YOLO 目标检测
        results = model(img)
        
        # 处理检测结果
        yolo_results = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = model.names[cls]
                
                if conf > 0.5:  # 置信度阈值
                    yolo_results.append({
                        "item_class": class_map.get(class_name, class_name),
                        "yolo_box": [x1, y1, x2, y2],
                        "confidence": conf
                    })
        
        # 构建返回数据
        if yolo_results:
            # 取置信度最高的结果
            best_result = max(yolo_results, key=lambda x: x['confidence'])
            data = {
                "item_class": best_result["item_class"],
                "yolo_box": best_result["yolo_box"],
                "ocr_text": ""
            }
        else:
            data = {
                "item_class": "未知",
                "yolo_box": [],
                "ocr_text": ""
            }
        
        return resp(data)
    except Exception as e:
        print(f"Error in recognize: {e}")
        raise HTTPException(status_code=500, detail=str(e))

