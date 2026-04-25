import io
import json
import os
import re
import time
import urllib.request
import uuid
from glob import glob
from datetime import datetime

from PIL import Image, ImageDraw
from sqlalchemy.orm import Session

from app.config import settings
from app.models.item import Item, ItemImage
from app.models.item_type import ItemType
from app.models.recognition_log import RecognitionLog

try:
    from ultralytics import YOLO
except Exception:
    YOLO = None

try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None


class AIService:
    _model = None
    _model_error = None

    def __init__(self, db: Session):
        self.db = db

    def _contract(self, cls: str, confidence: float, bbox: list[int], source: str):
        item_type = self.db.query(ItemType).filter(ItemType.code == cls).first()
        return {
            "item_class": cls,
            "confidence": round(confidence, 4),
            "bbox": bbox,
            "item_type_id": item_type.id if item_type else None,
            "item_type_name": item_type.name if item_type else None,
            "model_version": settings.ai_model_version,
            "source": source,
        }

    def _fetch_image(self, image_url: str):
        with urllib.request.urlopen(image_url, timeout=settings.ai_timeout_sec) as resp:
            content = resp.read()
        return Image.open(io.BytesIO(content))

    def _save_masked_image(self, image: Image.Image, ext: str = ".jpg") -> str:
        os.makedirs(settings.upload_dir, exist_ok=True)
        filename = f"masked_{uuid.uuid4().hex}{ext}"
        path = os.path.join(settings.upload_dir, filename)
        image.save(path)
        return f"{settings.base_url.rstrip('/')}/uploads/{filename}"

    def _should_mask_line(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return False
        if "姓名" in t:
            return False
        keywords = [
            "住址",
            "公民身份号码",
            "签发机关",
            "有效期限",
            "出生",
            "身份证号",
            "证号",
            "地址",
            # 学生证等新增字段：除姓名外也按敏感信息处理
            "学号",
            "学院",
            "专业",
            "班级",
            "年级",
            "入学",
            "有效期",
        ]
        if any(k in t for k in keywords):
            return True
        # 数字串（身份证号/学号/证件号）统一打码
        if re.search(r"\d{6,20}", t):
            return True
        if re.search(r"[A-Za-z]{1,4}\d{4,20}", t):
            return True
        return False

    def _is_name_line(self, text: str) -> bool:
        t = (text or "").strip()
        if not t:
            return False
        if "姓名" in t:
            return True
        # 纯中文短姓名，长度 2-4
        return re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", t) is not None

    def _box_to_rect(self, box):
        xs = [int(p[0]) for p in box]
        ys = [int(p[1]) for p in box]
        return [min(xs), min(ys), max(xs), max(ys)]

    def _build_paddle_ocr(self):
        from paddleocr import PaddleOCR

        # 兼容 PaddleOCR 新旧版本参数差异（如 show_log / enable_mkldnn）。
        candidates = [
            {"use_angle_cls": True, "lang": "ch", "use_gpu": False, "enable_mkldnn": False},
            {"use_angle_cls": True, "lang": "ch", "use_gpu": False},
            {"lang": "ch"},
            {},
        ]
        last_error = None
        for kwargs in candidates:
            try:
                return PaddleOCR(**kwargs)
            except Exception as exc:
                last_error = exc
                continue
        if last_error:
            raise last_error
        return PaddleOCR()

    def _rect_intersects(self, a, b) -> bool:
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 < bx1 or bx2 < ax1 or ay2 < by1 or by2 < ay1)

    def mask_id_card_image(self, image_row: ItemImage):
        try:
            img = self._fetch_image(image_row.image_url).convert("RGB")
            draw = ImageDraw.Draw(img)
            ocr_input = np.array(img) if np is not None else img
            ocr_rects = []
            keep_name_rects = []
            has_ocr = False

            # 1) OCR 框选敏感文本区域
            try:
                ocr = self._build_paddle_ocr()
                # 使用已下载的图像做 OCR，避免直接传 URL 导致偶发识别失败
                result = ocr.ocr(ocr_input, cls=True)
                if result and result[0]:
                    has_ocr = True
                    for line in result[0]:
                        if len(line) < 2:
                            continue
                        box = line[0]
                        text = line[1][0] if line[1] else ""
                        rect = self._box_to_rect(box)
                        ocr_rects.append(rect)
                        if self._is_name_line(text):
                            keep_name_rects.append(rect)
                        # 证件图默认“除姓名外全部打码”，保障学生证/身份证等字段统一脱敏
                        elif True:
                            draw.rectangle(rect, fill="black")
            except Exception:
                # OCR 不可用时继续执行人像遮挡和兜底区域遮挡
                pass

            # 2) 人像区域遮挡（OpenCV），若不可用则使用右上角兜底区域
            w, h = img.size
            if cv2 is not None and np is not None:
                arr = np.array(img)
                gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
                cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
                faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                for (x, y, fw, fh) in faces:
                    draw.rectangle([x, y, x + fw, y + fh], fill="black")
            else:
                # 身份证常见头像区域在右上
                draw.rectangle([int(w * 0.72), int(h * 0.08), int(w * 0.96), int(h * 0.42)], fill="black")

            # 3) 基于 OCR 文本框做“矩形栅格打码”：有文本且非姓名区域则打码
            if has_ocr and ocr_rects:
                cx1 = max(0, min(r[0] for r in ocr_rects) - 10)
                cy1 = max(0, min(r[1] for r in ocr_rects) - 10)
                cx2 = min(w, max(r[2] for r in ocr_rects) + 10)
                cy2 = min(h, max(r[3] for r in ocr_rects) + 10)
                cols, rows = 24, 14
                cell_w = max(1, (cx2 - cx1) // cols)
                cell_h = max(1, (cy2 - cy1) // rows)
                for r_i in range(rows):
                    for c_i in range(cols):
                        rx1 = cx1 + c_i * cell_w
                        ry1 = cy1 + r_i * cell_h
                        rx2 = cx2 if c_i == cols - 1 else rx1 + cell_w
                        ry2 = cy2 if r_i == rows - 1 else ry1 + cell_h
                        cell = [rx1, ry1, rx2, ry2]
                        has_text = any(self._rect_intersects(cell, t_rect) for t_rect in ocr_rects)
                        in_name = any(self._rect_intersects(cell, n_rect) for n_rect in keep_name_rects)
                        if has_text and not in_name:
                            draw.rectangle(cell, fill="black")
            else:
                # OCR 不稳定时的保底版式遮挡（优先保护隐私，宁可多遮挡）
                draw.rectangle([int(w * 0.25), int(h * 0.20), int(w * 0.62), int(h * 0.30)], fill="black")  # 性别/民族
                draw.rectangle([int(w * 0.25), int(h * 0.30), int(w * 0.72), int(h * 0.40)], fill="black")  # 出生
                draw.rectangle([int(w * 0.25), int(h * 0.40), int(w * 0.80), int(h * 0.68)], fill="black")  # 住址
                draw.rectangle([int(w * 0.28), int(h * 0.70), int(w * 0.96), int(h * 0.84)], fill="black")
                # 学生证常见布局：右半文本区 + 底部证号/学校区
                draw.rectangle([int(w * 0.48), int(h * 0.28), int(w * 0.95), int(h * 0.80)], fill="black")
                draw.rectangle([int(w * 0.16), int(h * 0.78), int(w * 0.96), int(h * 0.94)], fill="black")

            masked_url = self._save_masked_image(img, ext=".jpg")
            image_row.raw_image_url = image_row.raw_image_url or image_row.image_url
            image_row.masked_image_url = masked_url
            image_row.image_url = masked_url  # 前台默认只显示脱敏图
            image_row.is_sensitive = 1
            self.db.add(image_row)
            self.db.commit()
            self.db.refresh(image_row)
            return image_row, None
        except Exception as exc:
            return None, f"证件图脱敏失败: {exc}"

    @classmethod
    def _get_model(cls):
        if cls._model is not None or cls._model_error is not None:
            return cls._model
        if not settings.ai_enabled:
            cls._model_error = "AI disabled"
            return None
        if YOLO is None:
            cls._model_error = "ultralytics not installed"
            return None
        try:
            model_path = settings.ai_model_path
            if not os.path.isabs(model_path):
                model_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", model_path))
            if not os.path.exists(model_path):
                candidates = glob(os.path.join(os.path.dirname(__file__), "..", "..", "..", "yolo_model", "runs", "**", "weights", "best.pt"), recursive=True)
                if candidates:
                    model_path = candidates[0]
                else:
                    raise FileNotFoundError(f"未找到模型文件: {settings.ai_model_path}（也未找到 runs/**/weights/best.pt）")
            cls._model = YOLO(model_path)
        except Exception as exc:
            cls._model_error = str(exc)
            cls._model = None
        return cls._model

    def _infer_remote(self, image_url: str, conf_threshold: float):
        payload = json.dumps({"image_url": image_url, "conf_threshold": conf_threshold}).encode("utf-8")
        req = urllib.request.Request(
            url=f"{settings.ai_infer_url.rstrip('/')}/infer",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=settings.ai_timeout_sec) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        data = body.get("data") if isinstance(body, dict) else body
        return self._contract(
            cls=(data or {}).get("item_class", "unknown"),
            confidence=float((data or {}).get("confidence", 0)),
            bbox=(data or {}).get("bbox", []) or [],
            source="remote",
        )

    def _infer_local(self, image_url: str, conf_threshold: float):
        model = self._get_model()
        if model is None:
            raise RuntimeError(f"YOLO model unavailable: {self._model_error or 'unknown'}")
        img = self._fetch_image(image_url)
        # 统一走 CPU，避免本地 CUDA 环境不匹配导致识别失败
        results = model.predict(img, conf=conf_threshold, device="cpu", verbose=False)
        best = None
        for result in results:
            for box in result.boxes:
                conf = float(box.conf[0])
                if conf < conf_threshold:
                    continue
                cls_idx = int(box.cls[0])
                cls_name = model.names[cls_idx]
                xyxy = list(map(int, box.xyxy[0].tolist()))
                candidate = {"item_class": cls_name, "confidence": conf, "bbox": xyxy}
                if not best or candidate["confidence"] > best["confidence"]:
                    best = candidate
        if not best:
            best = {"item_class": "unknown", "confidence": 0.0, "bbox": []}
        return self._contract(best["item_class"], best["confidence"], best["bbox"], "local")

    def _log(self, item_id: int | None, image_id: int | None, input_info: dict, output_info: dict | None, cost_ms: int, status: str, error: str | None):
        row = RecognitionLog(
            item_id=item_id,
            image_id=image_id,
            model_type="yolo",
            model_version=settings.ai_model_version,
            status=status,
            input_info=input_info,
            output_info=output_info,
            error=error,
            cost_ms=cost_ms,
        )
        self.db.add(row)
        self.db.commit()

    def recognize_item(self, item_id: int, image_id: int | None, conf_threshold: float | None):
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None, "物品不存在"
        q = self.db.query(ItemImage).filter(ItemImage.item_id == item_id)
        if image_id:
            q = q.filter(ItemImage.id == image_id)
        image = q.order_by(ItemImage.sort_order.asc()).first()
        if not image:
            return None, "该物品暂无可识别图片"

        threshold = conf_threshold if conf_threshold is not None else settings.ai_conf_threshold
        start = time.time()
        try:
            if settings.ai_infer_url:
                try:
                    result = self._infer_remote(image.image_url, threshold)
                except Exception:
                    # 云推理失败时自动降级本地推理，保证主链路可用
                    result = self._infer_local(image.image_url, threshold)
            else:
                result = self._infer_local(image.image_url, threshold)
            image.ai_class = result["item_class"]
            image.ai_confidence = result["confidence"]
            image.ai_bbox_json = json.dumps(result["bbox"], ensure_ascii=False)
            image.ai_model_version = result["model_version"]
            image.ai_updated_at = datetime.now()
            image.yolo_type_id = result["item_type_id"]
            self.db.add(image)
            self.db.commit()
            self._log(
                item_id=item.id,
                image_id=image.id,
                input_info={"image_url": image.image_url, "conf_threshold": threshold},
                output_info=result,
                cost_ms=int((time.time() - start) * 1000),
                status="success",
                error=None,
            )
            return {
                "item_id": item.id,
                "image_id": image.id,
                **result,
            }, None
        except Exception as exc:
            self._log(
                item_id=item.id,
                image_id=image.id,
                input_info={"image_url": image.image_url, "conf_threshold": threshold},
                output_info=None,
                cost_ms=int((time.time() - start) * 1000),
                status="failed",
                error=str(exc),
            )
            return None, f"识别失败: {exc}"

    def recognize_image_url(self, image_url: str, conf_threshold: float | None):
        threshold = conf_threshold if conf_threshold is not None else settings.ai_conf_threshold
        start = time.time()
        try:
            if settings.ai_infer_url:
                try:
                    result = self._infer_remote(image_url, threshold)
                except Exception:
                    result = self._infer_local(image_url, threshold)
            else:
                result = self._infer_local(image_url, threshold)
            self._log(
                item_id=None,
                image_id=None,
                input_info={"image_url": image_url, "conf_threshold": threshold},
                output_info=result,
                cost_ms=int((time.time() - start) * 1000),
                status="success",
                error=None,
            )
            return result, None
        except Exception as exc:
            self._log(
                item_id=None,
                image_id=None,
                input_info={"image_url": image_url, "conf_threshold": threshold},
                output_info=None,
                cost_ms=int((time.time() - start) * 1000),
                status="failed",
                error=str(exc),
            )
            return None, f"识别失败: {exc}"

    def health(self):
        remote = bool(settings.ai_infer_url)
        local_model_ready = self._get_model() is not None
        return {
            "remote_enabled": remote,
            "local_model_ready": local_model_ready,
            "model_version": settings.ai_model_version,
            "timeout_sec": settings.ai_timeout_sec,
        }

    def recognize_id_card_text(self, image_url: str):
        text_blocks = []
        ocr_error = ""
        try:
            ocr = self._build_paddle_ocr()
            # 先拉取图片再识别，避免 OCR 直接读取 URL 在部分环境下拿不到内容
            # 优先传 numpy 数组；若 numpy 不可用则降级为本地临时文件路径。
            img = self._fetch_image(image_url).convert("RGB")
            if np is not None:
                arr = np.array(img)
                result = ocr.ocr(arr, cls=True)
            else:
                os.makedirs(settings.upload_dir, exist_ok=True)
                tmp_path = os.path.join(settings.upload_dir, f"ocr_tmp_{uuid.uuid4().hex}.jpg")
                try:
                    img.save(tmp_path)
                    result = ocr.ocr(tmp_path, cls=True)
                finally:
                    try:
                        if os.path.exists(tmp_path):
                            os.remove(tmp_path)
                    except Exception:
                        pass
            if result and result[0]:
                for line in result[0]:
                    if len(line) >= 2 and len(line[1]) >= 1:
                        text_blocks.append(line[1][0])
        except Exception as exc:
            # OCR 模型不可用时，返回空结果给前端手动补录，并透出错误用于排查
            ocr_error = str(exc)
            text_blocks = []

        full = "\n".join([t.strip() for t in text_blocks if t and t.strip()])
        name = ""
        id_no = ""
        student_no = ""
        college = ""
        major = ""
        address = ""
        doc_type = "id_card"

        normalized_full = re.sub(r"\s+", "", full).replace("O", "0").replace("o", "0")
        m_id = re.search(r"(\d{17}[0-9Xx])", normalized_full)
        if m_id:
            id_no = m_id.group(1).upper()
        student_keywords = ("学生证", "学号", "学院", "专业", "班级")
        if any(k in full for k in student_keywords):
            doc_type = "campus_card"
        if not id_no:
            m_student = re.search(r"(?:学号|证号)[:：]?\s*([A-Za-z0-9]{6,20})", full)
            if m_student:
                student_no = m_student.group(1).strip()
                doc_type = "campus_card"
        m_college = re.search(r"(?:学院|院系)[:：]?\s*([^\n]{2,40})", full)
        if m_college:
            college = m_college.group(1).strip()
            doc_type = "campus_card"
        m_major = re.search(r"(?:专业)[:：]?\s*([^\n]{2,40})", full)
        if m_major:
            major = m_major.group(1).strip()
            doc_type = "campus_card"
        m_name = re.search(r"姓名[:：]?\s*([^\n]{1,8})", full)
        if m_name:
            name = m_name.group(1).strip()
        else:
            for line in text_blocks:
                if "姓名" in line and len(line) <= 16:
                    name = line.replace("姓名", "").replace(":", "").replace("：", "").strip()
                    if name:
                        break
        if not name:
            # 兜底：在 OCR 行里找 2-4 位中文人名（排除常见字段词）
            for line in text_blocks:
                s = re.sub(r"\s+", "", line)
                if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", s) and s not in {"中华人民共和国", "居民身份证", "姓名", "住址", "性别", "民族"}:
                    name = s
                    break
        m_addr = re.search(r"住址[:：]?\s*([^\n]{4,80})", full)
        if m_addr:
            address = m_addr.group(1).strip()
        elif "住址" in full:
            # 兜底：从“住址”所在行后拼接多行地址文本
            lines = [re.sub(r"\s+", "", t or "") for t in text_blocks]
            for idx, ln in enumerate(lines):
                if "住址" in ln:
                    addr = ln.split("住址", 1)[-1].replace(":", "").replace("：", "")
                    j = idx + 1
                    while j < len(lines) and lines[j] and not re.search(r"\d{17}[0-9Xx]", lines[j]):
                        addr += lines[j]
                        if len(addr) >= 80:
                            break
                        j += 1
                    address = addr[:80]
                    break
        present_fields = []
        if name:
            present_fields.append("name")
        if id_no:
            present_fields.append("id_no")
        if student_no:
            present_fields.append("student_no")
        if address:
            present_fields.append("address")
        if college:
            present_fields.append("college")
        if major:
            present_fields.append("major")
        return {
            "name": name,
            "id_no": id_no,
            "student_no": student_no,
            "college": college,
            "major": major,
            "address": address,
            "doc_type": doc_type,
            "present_fields": present_fields,
            "raw_text": full[:1000],
            "has_result": bool(name or id_no or student_no or address),
            "ocr_error": ocr_error,
        }

    def apply_suggestion(self, user_id: int, item_id: int, item_type_id: int):
        item = self.db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None, "物品不存在"
        if item.user_id != user_id:
            return None, "仅发布者可采用识别建议"
        item_type = self.db.query(ItemType).filter(ItemType.id == item_type_id).first()
        if not item_type:
            return None, "识别建议分类不存在"
        item.item_type_id = item_type_id
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return {
            "item_id": item.id,
            "item_type_id": item.item_type_id,
            "item_type_name": item_type.name,
        }, None
