from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.media_url import normalize_media_url
from app.models.behavior_log import BehaviorLog
from app.models.item import Item, ItemImage
from app.repositories.item_repository import ItemRepository
from app.services.clip_service import ClipService


# 隐式反馈权重（协同过滤共现强度）
BEHAVIOR_WEIGHTS: dict[str, float] = {
    "view": 0.35,
    "click_detail": 1.0,
    "favorite": 3.0,
    "click_contact": 4.0,
    "comment": 2.0,
    "search": 0.5,
}

# 融合：内容相似（CLIP）与协同分数
WEIGHT_CLIP = 0.58
WEIGHT_CF = 0.42


class RecommendService:
    def __init__(self, db: Session):
        self.db = db
        self.item_repo = ItemRepository(db)

    def log_behavior(
        self,
        user_id: int | None,
        item_id: int,
        behavior_type: str,
        extra: dict | None = None,
    ) -> None:
        if behavior_type not in BEHAVIOR_WEIGHTS:
            behavior_type = "view"
        row = BehaviorLog(
            user_id=user_id,
            item_id=item_id,
            behavior_type=behavior_type,
            extra=extra,
        )
        self.db.add(row)
        self.db.commit()

    def collaborative_scores(self, anchor_item_id: int, max_users: int = 500) -> dict[int, float]:
        """基于用户的 Item-Item 协同：与看过锚点物品的用户还交互过的其它物品，加权求和。"""
        uid_rows = (
            self.db.query(BehaviorLog.user_id)
            .filter(BehaviorLog.item_id == anchor_item_id, BehaviorLog.user_id.isnot(None))
            .distinct()
            .limit(max_users)
            .all()
        )
        user_ids = [r[0] for r in uid_rows if r[0]]
        if not user_ids:
            return {}
        rows = (
            self.db.query(BehaviorLog)
            .filter(
                BehaviorLog.user_id.in_(user_ids),
                BehaviorLog.item_id != anchor_item_id,
            )
            .all()
        )
        scores: dict[int, float] = defaultdict(float)
        for r in rows:
            w = BEHAVIOR_WEIGHTS.get(r.behavior_type, 0.25)
            scores[r.item_id] += w
        return dict(scores)

    def _normalize_scores(self, raw: dict[int, float]) -> dict[int, float]:
        if not raw:
            return {}
        m = max(raw.values()) or 1.0
        return {k: v / m for k, v in raw.items()}

    def _fallback_recent(self, anchor: Item, exclude: set[int], limit: int) -> list[dict]:
        now = datetime.now()
        q = self.db.query(Item).filter(
            Item.item_type == anchor.item_type,
            Item.status == 1,
            Item.is_deleted == 0,
            Item.id != anchor.id,
            or_(Item.expires_at.is_(None), Item.expires_at >= now),
        )
        if exclude:
            q = q.filter(~Item.id.in_(exclude))
        items = q.order_by(Item.created_at.desc()).limit(limit).all()
        out = []
        for it in items:
            imgs = self.item_repo.get_item_images(it.id)
            out.append(
                {
                    "id": it.id,
                    "item_type": it.item_type,
                    "item_type_id": it.item_type_id,
                    "title": it.title,
                    "cover_image": normalize_media_url(imgs[0].image_url) if imgs else "",
                    "similarity": 0.15,
                    "cf_score": 0.0,
                    "blend_score": 0.15,
                    "source": "recent",
                    "location_name": it.location_detail or "",
                    "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
                    "status": it.status,
                    "status_label": ClipService._status_label(it.item_type, it.status),
                }
            )
        return out

    def related_items(self, anchor_item_id: int, limit: int = 10) -> dict:
        anchor = self.item_repo.get_item(anchor_item_id)
        if not anchor or anchor.is_deleted:
            return {"list": [], "anchor_id": anchor_item_id, "note": "物品不存在"}

        clip_svc = ClipService(self.db)
        clip_rows = clip_svc.similar_to_item(anchor_item_id, top_k=max(60, limit * 6))
        clip_by_id = {r["id"]: float(r["similarity"]) for r in clip_rows}

        cf_raw = self.collaborative_scores(anchor_item_id)
        cf_norm = self._normalize_scores(cf_raw)

        candidate_ids = set(clip_by_id) | set(cf_norm)
        candidate_ids.discard(anchor_item_id)

        blended: list[tuple[int, float, float, float, str]] = []
        for iid in candidate_ids:
            it = self.item_repo.get_item(iid)
            if not it or it.is_deleted or it.status != 1:
                continue
            if it.expires_at and it.expires_at < datetime.now():
                continue
            c_clip = clip_by_id.get(iid, 0.0)
            c_cf = cf_norm.get(iid, 0.0)
            if c_clip > 0 and c_cf > 0:
                src = "hybrid"
            elif c_clip > 0:
                src = "clip"
            else:
                src = "cf"
            blend = WEIGHT_CLIP * c_clip + WEIGHT_CF * c_cf
            blended.append((iid, blend, c_clip, c_cf, src))

        blended.sort(key=lambda x: x[1], reverse=True)

        list_out: list[dict] = []
        seen: set[int] = set()
        for iid, blend, c_clip, c_cf, src in blended:
            if iid in seen:
                continue
            if len(list_out) >= limit:
                break
            it = self.item_repo.get_item(iid)
            if not it:
                continue
            imgs = self.item_repo.get_item_images(it.id)
            clip_row = next((r for r in clip_rows if r["id"] == iid), None)
            list_out.append(
                {
                    "id": it.id,
                    "item_type": it.item_type,
                    "item_type_id": it.item_type_id,
                    "title": it.title,
                    "cover_image": normalize_media_url(imgs[0].image_url if imgs else (clip_row or {}).get("cover_image", "")),
                    "similarity": round(c_clip, 4),
                    "cf_score": round(c_cf, 4),
                    "blend_score": round(blend, 4),
                    "source": src,
                    "location_name": it.location_detail or "",
                    "lost_found_time": str(it.lost_found_time) if it.lost_found_time else "",
                    "status": it.status,
                    "status_label": ClipService._status_label(it.item_type, it.status),
                }
            )
            seen.add(iid)

        note_parts = []
        if not clip_by_id:
            note_parts.append("无CLIP特征时以协同与近期为主")
        if not cf_norm:
            note_parts.append("协同数据不足时以内容相似为主")

        if len(list_out) < limit:
            fb = self._fallback_recent(anchor, {anchor_item_id} | seen, limit - len(list_out))
            list_out.extend(fb)

        return {
            "list": list_out[:limit],
            "anchor_id": anchor_item_id,
            "note": "；".join(note_parts) if note_parts else "ok",
        }
