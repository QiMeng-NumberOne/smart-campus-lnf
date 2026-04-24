import io

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from PIL import Image
from ultralytics import YOLO
import urllib.request

MODEL_PATH = "../yolo_model/yolo26n.pt"
MODEL_VERSION = "campus_yolo_v1"
DEFAULT_THRESHOLD = 0.5

app = FastAPI(title="Campus YOLO Inference Service", version="1.0.0")
model = YOLO(MODEL_PATH)


class InferBody(BaseModel):
    image_url: str
    conf_threshold: float = DEFAULT_THRESHOLD


def _fetch_image(url: str):
    with urllib.request.urlopen(url, timeout=5) as resp:
        content = resp.read()
    return Image.open(io.BytesIO(content))


@app.get("/health")
def health():
    return {"code": 0, "message": "success", "data": {"model_version": MODEL_VERSION}}


@app.post("/infer")
def infer(body: InferBody):
    try:
        image = _fetch_image(body.image_url)
        results = model(image)
        best = {"item_class": "unknown", "confidence": 0.0, "bbox": []}
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < body.conf_threshold:
                    continue
                cls_idx = int(box.cls[0])
                cls_name = model.names[cls_idx]
                xyxy = list(map(int, box.xyxy[0].tolist()))
                if conf > best["confidence"]:
                    best = {"item_class": cls_name, "confidence": conf, "bbox": xyxy}
        return {"code": 0, "message": "success", "data": best}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
