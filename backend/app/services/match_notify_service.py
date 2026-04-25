import json
from datetime import datetime

import numpy as np
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.item import Item
from app.models.item_feature import FEATURE_TYPE_CLIP_BUNDLE, ItemFeature
from app.repositories.message_repository import MessageRepository
from app.models.user import User
from app.services.wechat_subscribe_service import WechatSubscribeService


MATCH_THRESHOLD = 0.90
MATCH_TOPK = 5


class MatchNotifyService:
    MATCH_PREFIX = "[MATCH_JSON]"

    def __init__(self, db: Session):
        self.db = db
        self.msg_repo = MessageRepository(db)

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        denom = float(np.linalg.norm(a) * np.linalg.norm(b))
        if denom == 0:
            return 0.0
        return float(np.dot(a, b) / denom)

    def _load_feature(self, item_id: int):
        row = (
            self.db.query(ItemFeature)
            .filter(ItemFeature.item_id == item_id, ItemFeature.feature_type == FEATURE_TYPE_CLIP_BUNDLE)
            .first()
        )
        if not row:
            return None
        vec = row.feature_vector
        if isinstance(vec, str):
            vec = json.loads(vec)
        if not isinstance(vec, dict):
            return None
        iv = np.asarray(vec.get("image", []), dtype=np.float32)
        tv = np.asarray(vec.get("text", []), dtype=np.float32)
        if iv.size == 0 or tv.size == 0:
            return None
        return {"image": iv, "text": tv}

    def _encode_match_payload(
        self,
        message_text: str,
        source_item_id: int,
        target_item_id: int,
        similarity: float,
    ) -> str:
        return self.MATCH_PREFIX + json.dumps(
            {
                "text": message_text,
                "source_item_id": source_item_id,
                "target_item_id": target_item_id,
                "similarity": round(similarity, 4),
            },
            ensure_ascii=False,
        )

    def _message_exists(self, to_user_id: int, owner_item_id: int, target_item_id: int) -> bool:
        from app.models.message import Message

        marker = f"\"target_item_id\": {target_item_id}"
        row = (
            self.db.query(Message.id)
            .filter(
                Message.to_user_id == to_user_id,
                Message.item_id == owner_item_id,
                or_(
                    Message.content.like(f"{self.MATCH_PREFIX}%"),
                    Message.content.like("[匹配JSON]%"),
                    Message.content.like("[ƥ��JSON]%"),
                ),
                Message.content.like(f"%{marker}%"),
            )
            .first()
        )
        return row is not None

    def notify_for_new_item(self, item_id: int) -> int:
        """新发帖后自动匹配，命中>=90%则写入站内匹配通知，返回新增通知条数。"""
        source = self.db.query(Item).filter(Item.id == item_id, Item.is_deleted == 0, Item.status == 1).first()
        if not source:
            return 0
        source_feat = self._load_feature(source.id)
        if not source_feat:
            return 0

        now = datetime.now()
        if source.item_type == 1:
            # 新寻物：匹配招领，通知当前寻物发布者
            target_q = (
                self.db.query(Item)
                .filter(
                    Item.item_type == 2,
                    Item.status == 1,
                    Item.is_deleted == 0,
                    Item.id != source.id,
                    ((Item.expires_at == None) | (Item.expires_at >= now)),
                )
                .all()
            )
        else:
            # 新招领：匹配寻物，通知寻物发布者
            target_q = (
                self.db.query(Item)
                .filter(
                    Item.item_type == 1,
                    Item.status == 1,
                    Item.is_deleted == 0,
                    Item.id != source.id,
                    ((Item.expires_at == None) | (Item.expires_at >= now)),
                )
                .all()
            )

        scored = []
        for tgt in target_q:
            tgt_feat = self._load_feature(tgt.id)
            if not tgt_feat:
                continue
            image_sim = self._cosine(source_feat["image"], tgt_feat["image"])
            # 只按图片相似度触发匹配通知（业务口径：图像>=90%即通知）
            effective_sim = image_sim
            if effective_sim >= MATCH_THRESHOLD:
                scored.append((tgt, effective_sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        scored = scored[:MATCH_TOPK]

        created = 0
        for tgt, sim in scored:
            if source.item_type == 1:
                # 寻物本人收到“疑似对应招领”
                to_user_id = source.user_id
                owner_item_id = source.id
                target_item_id = tgt.id
                from_user_id = tgt.user_id
                text = (
                    f"匹配通知：检测到一条招领帖可能是您在找的物品，"
                    f"匹配度{round(sim * 100, 1)}%。点击查看详情并联系发布者。"
                )
            else:
                # 寻物发布者收到“疑似对应招领”
                to_user_id = tgt.user_id
                owner_item_id = tgt.id
                target_item_id = source.id
                from_user_id = source.user_id
                text = (
                    f"匹配通知：有一条新的招领帖与您的寻物帖高度相似，"
                    f"匹配度{round(sim * 100, 1)}%。点击查看详情并联系发布者。"
                )

            if self._message_exists(to_user_id, owner_item_id, target_item_id):
                continue

            payload = self._encode_match_payload(text, owner_item_id, target_item_id, sim)
            self.msg_repo.create(
                from_user_id=from_user_id,
                to_user_id=to_user_id,
                item_id=owner_item_id,
                content=payload,
            )
            # 微信订阅消息（离线可见）；失败不影响站内消息
            user = self.db.query(User).filter(User.id == to_user_id).first()
            WechatSubscribeService.send_match_notification(
                user=user, target_item_id=target_item_id, similarity=sim
            )
            created += 1
        return created
