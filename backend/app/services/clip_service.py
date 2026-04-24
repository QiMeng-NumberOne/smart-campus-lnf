import io
import os
import urllib.request
from urllib.parse import urlparse
from typing import Optional

import numpy as np
from PIL import Image
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.item import Item, ItemImage
from app.models.item_feature import FEATURE_TYPE_CLIP_BUNDLE, ItemFeature


class ClipService:
    _loaded = False
    _model = None
    _preprocess = None
    _tokenize = None
    _torch = None
    _device = "cpu"
    _load_error = None
    _backend = None

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _model_key() -> str:
        b = ClipService._backend or "na"
        return f"{b}_{settings.clip_model_name}"

    @staticmethod
    def _status_label(item_type: int, status: int) -> str:
        if item_type == 1:
            return {1: "未找回", 2: "已找回", 3: "已关闭"}.get(status, "未知")
        return {1: "未认领", 2: "已认领", 3: "已关闭"}.get(status, "未知")

    @staticmethod
    def _upload_dir_abs() -> str:
        return os.path.abspath(settings.upload_dir)

    @classmethod
    def refresh_item_features(cls, db: Session, item_id: int) -> bool:
        """写入或更新单条物品特征（多图向量平均再归一化）；与库表 feature_vector(JSON) 一致。"""
        import logging

        log = logging.getLogger(__name__)
        try:
            cls._load_model()
            if cls._model is None:
                return False
            item = db.query(Item).filter(Item.id == item_id, Item.is_deleted == 0).first()
            if not item:
                return False
            images = (
                db.query(ItemImage)
                .filter(ItemImage.item_id == item_id)
                .order_by(ItemImage.sort_order.asc())
                .all()
            )
            if not images:
                db.query(ItemFeature).filter(ItemFeature.item_id == item_id).delete()
                db.commit()
                return False
            svc = cls(db)
            img_vecs: list[np.ndarray] = []
            for im in images:
                try:
                    pil = svc._fetch_image_from_url(im.image_url)
                    img_vecs.append(svc._encode_image(pil))
                except Exception:
                    continue
            if not img_vecs:
                db.query(ItemFeature).filter(ItemFeature.item_id == item_id).delete()
                db.commit()
                return False
            stacked = np.stack(img_vecs, axis=0)
            img_vec = stacked.mean(axis=0)
            nrm = float(np.linalg.norm(img_vec)) + 1e-8
            img_vec = img_vec / nrm
            text = f"{item.title or ''} {item.description or ''}".strip() or (item.title or "物品")
            txt_vec = svc._encode_text(text)
            dim = int(img_vec.shape[0])
            mk = cls._model_key()
            payload = {
                "image": img_vec.astype(float).tolist(),
                "text": txt_vec.astype(float).tolist(),
                "dim": dim,
                "model_key": mk,
            }
            db.query(ItemFeature).filter(ItemFeature.item_id == item_id).delete()
            db.add(
                ItemFeature(
                    item_id=item_id,
                    image_id=images[0].id if images else None,
                    feature_type=FEATURE_TYPE_CLIP_BUNDLE,
                    feature_vector=payload,
                )
            )
            db.commit()
            return True
        except Exception as exc:
            db.rollback()
            log.warning("refresh_item_features failed item_id=%s: %s", item_id, exc)
            return False

    @classmethod
    def _load_model(cls):
        if cls._loaded:
            return
        cls._loaded = True
        try:
            import torch
            cls._torch = torch
            cls._device = "cuda" if (settings.clip_device == "auto" and torch.cuda.is_available()) else "cpu"
            if settings.clip_device in ("cpu", "cuda"):
                cls._device = settings.clip_device
            try:
                import cn_clip.clip as clip
                from cn_clip.clip import load_from_name

                # 优先尝试 modelscope 下载（与官方示例一致），失败则回退到默认下载逻辑
                try:
                    model, preprocess = load_from_name(
                        settings.clip_model_name,
                        device=cls._device,
                        download_root=settings.clip_model_root or None,
                        use_modelscope=True,
                    )
                except Exception:
                    model, preprocess = load_from_name(
                        settings.clip_model_name,
                        device=cls._device,
                        download_root=settings.clip_model_root or None,
                    )
                model.eval()
                cls._model = model
                cls._preprocess = preprocess
                cls._tokenize = clip.tokenize
                cls._backend = "cn_clip"
            except Exception:
                # Windows 下 cn_clip 依赖（lmdb）安装失败时，回退到 Transformers ChineseCLIP
                from transformers import ChineseCLIPModel, ChineseCLIPProcessor

                model_id = settings.clip_model_root or "OFA-Sys/chinese-clip-vit-large-patch14"
                model = ChineseCLIPModel.from_pretrained(model_id, use_safetensors=True)
                processor = ChineseCLIPProcessor.from_pretrained(model_id)
                model.to(cls._device)
                model.eval()
                cls._model = model
                cls._preprocess = processor
                cls._tokenize = None
                cls._backend = "transformers"
        except Exception as exc:
            cls._load_error = str(exc)

    @classmethod
    def load_error(cls) -> Optional[str]:
        cls._load_model()
        # Allow recovery without full process restart after environment fixes.
        if cls._model is None and cls._load_error:
            cls._loaded = False
            cls._load_error = None
            cls._load_model()
        return cls._load_error

    @classmethod
    def runtime_info(cls) -> dict:
        cls._load_model()
        return {
            "loaded": cls._model is not None,
            "backend": cls._backend,
            "device": cls._device,
            "error": cls._load_error,
            "model_name": settings.clip_model_name,
            "model_root": settings.clip_model_root,
        }

    def _fetch_image_from_url(self, url: str) -> Image.Image:
        if not url:
            raise ValueError("empty image url")
        # Always prefer local upload path resolution so host/port changes do not break retrieval.
        if "/uploads/" in url:
            filename = url.split("/uploads/", 1)[1].split("?", 1)[0]
            filename = os.path.basename(filename)
            local_path = os.path.join(ClipService._upload_dir_abs(), filename)
            if os.path.exists(local_path):
                return Image.open(local_path).convert("RGB")
        prefix = f"{settings.base_url.rstrip('/')}/uploads/"
        if url.startswith(prefix):
            filename = url.replace(prefix, "", 1)
            path = os.path.join(ClipService._upload_dir_abs(), filename)
            if os.path.exists(path):
                return Image.open(path).convert("RGB")
        parsed = urlparse(url)
        if parsed.scheme in ("", "file"):
            maybe_path = parsed.path or url
            if os.path.exists(maybe_path):
                return Image.open(maybe_path).convert("RGB")
        with urllib.request.urlopen(url, timeout=settings.ai_timeout_sec) as resp:
            content = resp.read()
        return Image.open(io.BytesIO(content)).convert("RGB")

    def _encode_image(self, image: Image.Image) -> np.ndarray:
        self._load_model()
        if self._model is None:
            raise RuntimeError(self._load_error or "CLIP model unavailable")
        torch = self._torch
        with torch.no_grad():
            if self._backend == "cn_clip":
                tensor = self._preprocess(image).unsqueeze(0).to(self._device)
                vec = self._model.encode_image(tensor)
            else:
                inputs = self._preprocess(images=image, return_tensors="pt")
                inputs = {k: v.to(self._device) for k, v in inputs.items()}
                vec = self._model.get_image_features(**inputs)
            vec = vec / vec.norm(dim=-1, keepdim=True)
        return vec.cpu().numpy()[0]

    def _encode_text(self, text: str) -> np.ndarray:
        self._load_model()
        if self._model is None:
            raise RuntimeError(self._load_error or "CLIP model unavailable")
        torch = self._torch
        with torch.no_grad():
            if self._backend == "cn_clip":
                token_fn = self.__class__._tokenize
                tokens = token_fn([text], context_length=52).to(self._device)
                vec = self._model.encode_text(tokens)
            else:
                inputs = self._preprocess(text=[text], padding=True, return_tensors="pt")
                inputs = {k: v.to(self._device) for k, v in inputs.items()}
                vec = self._model.get_text_features(**inputs)
            vec = vec / vec.norm(dim=-1, keepdim=True)
        return vec.cpu().numpy()[0]

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def _candidate_items(self, item_type: Optional[int], item_type_id: Optional[int], limit: int = 100):
        q = self.db.query(Item).filter(and_(Item.status == 1, Item.is_deleted == 0))
        if item_type is not None:
            q = q.filter(Item.item_type == item_type)
        if item_type_id:
            q = q.filter(Item.item_type_id == item_type_id)
        return q.order_by(Item.created_at.desc()).limit(limit).all()

    def _candidate_limit_legacy(self, item_type: Optional[int], item_type_id: Optional[int]) -> int:
        """无分类筛选时放宽条数，避免只扫最近寻物启事。"""
        if item_type is None and not item_type_id:
            return 2000
        return 120

    def _item_cover(self, item_id: int):
        return self.db.query(ItemImage).filter(ItemImage.item_id == item_id).order_by(ItemImage.sort_order.asc()).first()

    def _features_join_query(self, item_type: Optional[int], item_type_id: Optional[int]):
        q = (
            self.db.query(ItemFeature, Item)
            .join(Item, Item.id == ItemFeature.item_id)
            .filter(
                and_(
                    Item.status == 1,
                    Item.is_deleted == 0,
                    ItemFeature.feature_type == FEATURE_TYPE_CLIP_BUNDLE,
                )
            )
        )
        if item_type is not None:
            q = q.filter(Item.item_type == item_type)
        if item_type_id:
            q = q.filter(Item.item_type_id == item_type_id)
        return q

    def _cover_map(self, item_ids: list) -> dict:
        if not item_ids:
            return {}
        covers = {}
        imgs = (
            self.db.query(ItemImage)
            .filter(ItemImage.item_id.in_(item_ids))
            .order_by(ItemImage.item_id.asc(), ItemImage.sort_order.asc())
            .all()
        )
        for img in imgs:
            if img.item_id not in covers:
                covers[img.item_id] = img.image_url
        return covers

    def _row_dict(self, it: Item, cover_url: str, sim: float) -> dict:
        return {
            "id": it.id,
            "item_type": it.item_type,
            "item_type_id": it.item_type_id,
            "title": it.title,
            "cover_image": cover_url,
            "similarity": round(max(0.0, min(1.0, sim)), 4),
            "location_name": it.location_detail or "",
            "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
            "status": it.status,
            "status_label": self._status_label(it.item_type, it.status),
        }

    def _feature_index_count(self, item_type: Optional[int], item_type_id: Optional[int]) -> int:
        return self._features_join_query(item_type, item_type_id).count()

    def _feature_compatible(self, vec: dict) -> bool:
        mk = vec.get("model_key")
        if not mk:
            return False
        return mk == self._model_key()

    def search_by_image(self, image: Image.Image, item_type: Optional[int], item_type_id: Optional[int], top_k: int = 20):
        query_vec = self._encode_image(image)
        note = ""
        if self._feature_index_count(item_type, item_type_id) > 0:
            rows = self._search_by_image_features(query_vec, item_type, item_type_id, top_k)
            if rows:
                return rows, note
            note = "特征库无命中，已回退实时计算"
        return self._search_by_image_legacy(query_vec, item_type, item_type_id, top_k), note

    def _search_by_image_features(
        self, query_vec: np.ndarray, item_type: Optional[int], item_type_id: Optional[int], top_k: int
    ):
        pairs = self._features_join_query(item_type, item_type_id).all()
        if not pairs:
            return []
        ids = [it.id for _, it in pairs]
        covers = self._cover_map(ids)
        rows = []
        for feat, it in pairs:
            try:
                vec = feat.feature_vector
                if isinstance(vec, str):
                    import json

                    vec = json.loads(vec)
                if not isinstance(vec, dict):
                    continue
                if not self._feature_compatible(vec):
                    continue
                iv = np.asarray(vec.get("image", []), dtype=np.float32)
                tv = np.asarray(vec.get("text", []), dtype=np.float32)
                if iv.size == 0 or tv.size == 0:
                    continue
                sim = 0.88 * self._cosine(query_vec, iv) + 0.12 * self._cosine(query_vec, tv)
                cu = covers.get(it.id, "")
                rows.append(self._row_dict(it, cu, sim))
            except Exception:
                continue
        rows.sort(key=lambda x: x["similarity"], reverse=True)
        return rows[:top_k]

    def _search_by_image_legacy(
        self, query_vec: np.ndarray, item_type: Optional[int], item_type_id: Optional[int], top_k: int
    ):
        lim = self._candidate_limit_legacy(item_type, item_type_id)
        items = self._candidate_items(item_type, item_type_id, limit=lim)
        rows = []
        for it in items:
            cover = self._item_cover(it.id)
            if not cover:
                continue
            try:
                img_vec = self._encode_image(self._fetch_image_from_url(cover.image_url))
                txt_vec = self._encode_text(f"{it.title or ''} {it.description or ''}".strip())
                sim = 0.88 * self._cosine(query_vec, img_vec) + 0.12 * self._cosine(query_vec, txt_vec)
                rows.append(self._row_dict(it, cover.image_url, sim))
            except Exception:
                continue
        rows.sort(key=lambda x: x["similarity"], reverse=True)
        return rows[:top_k]

    def search_by_text(self, keyword: str, item_type: Optional[int], item_type_id: Optional[int], top_k: int = 20):
        q_vec = self._encode_text(keyword)
        note = ""
        if self._feature_index_count(item_type, item_type_id) > 0:
            rows = self._search_by_text_features(q_vec, item_type, item_type_id, top_k)
            if rows:
                return rows, note
            note = "特征库无命中，已回退实时计算"
        return self._search_by_text_legacy(q_vec, item_type, item_type_id, top_k), note

    def _search_by_text_features(
        self, q_vec: np.ndarray, item_type: Optional[int], item_type_id: Optional[int], top_k: int
    ):
        pairs = self._features_join_query(item_type, item_type_id).all()
        if not pairs:
            return []
        ids = [it.id for _, it in pairs]
        covers = self._cover_map(ids)
        rows = []
        for feat, it in pairs:
            try:
                vec = feat.feature_vector
                if isinstance(vec, str):
                    import json

                    vec = json.loads(vec)
                if not isinstance(vec, dict):
                    continue
                if not self._feature_compatible(vec):
                    continue
                txt_v = np.asarray(vec.get("text", []), dtype=np.float32)
                img_v = np.asarray(vec.get("image", []), dtype=np.float32)
                if txt_v.size == 0 or img_v.size == 0:
                    continue
                sim = 0.72 * self._cosine(q_vec, txt_v) + 0.28 * self._cosine(q_vec, img_v)
                cu = covers.get(it.id, "")
                rows.append(self._row_dict(it, cu, sim))
            except Exception:
                continue
        rows.sort(key=lambda x: x["similarity"], reverse=True)
        return rows[:top_k]

    def _search_by_text_legacy(
        self, q_vec: np.ndarray, item_type: Optional[int], item_type_id: Optional[int], top_k: int
    ):
        lim = self._candidate_limit_legacy(item_type, item_type_id)
        items = self._candidate_items(item_type, item_type_id, limit=lim)
        rows = []
        for it in items:
            cover = self._item_cover(it.id)
            if not cover:
                continue
            try:
                txt_vec = self._encode_text(f"{it.title or ''} {it.description or ''}".strip())
                img_vec = self._encode_image(self._fetch_image_from_url(cover.image_url))
                sim = 0.72 * self._cosine(q_vec, txt_vec) + 0.28 * self._cosine(q_vec, img_vec)
                rows.append(self._row_dict(it, cover.image_url, sim))
            except Exception:
                continue
        rows.sort(key=lambda x: x["similarity"], reverse=True)
        return rows[:top_k]
