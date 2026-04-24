from datetime import datetime
from datetime import timedelta
import logging

from app.models.item import Item, ItemImage
from app.repositories.item_repository import ItemRepository
from app.schemas.item import ItemCreate
from app.core.crypto import encrypt_text
from app.services.ai_service import AIService


def _parse_datetime(value: str | None):
    if not value:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


class ItemService:
    def __init__(self, repo: ItemRepository):
        self.repo = repo

    def _status_label(self, item_type: int, status: int) -> str:
        if item_type == 1:
            return {1: "未找回", 2: "已找回", 3: "已关闭"}.get(status, "未知")
        return {1: "未认领", 2: "已认领", 3: "已关闭"}.get(status, "未知")

    def create_item(self, user_id: int, body: ItemCreate):
        is_cert_item = bool(body.item_type_id == 9 or body.id_card_info is not None)
        item = Item(
            user_id=user_id,
            item_type=body.item_type,
            item_type_id=9 if is_cert_item else body.item_type_id,
            title=body.title,
            description=body.description,
            status=1,
            is_deleted=0,
            location_id=body.location_id,
            location_detail=body.location_detail,
            lost_found_time=_parse_datetime(body.lost_found_time),
            expires_at=datetime.now() + timedelta(days=28),
            contact_info=body.contact_info,
        )
        item = self.repo.create_item(item)
        images = [ItemImage(item_id=item.id, image_url=img.url, sort_order=i) for i, img in enumerate(body.images)]
        if images:
            self.repo.add_images(images)
        if is_cert_item:
            image_rows = self.repo.get_item_images(item.id)
            ai_service = AIService(self.repo.db)
            for row in image_rows:
                _, mask_err = ai_service.mask_id_card_image(row)
                if mask_err:
                    logging.getLogger(__name__).warning("mask cert image failed item_id=%s image_id=%s: %s", item.id, row.id, mask_err)
        if body.id_card_info and is_cert_item:
            info = body.id_card_info
            cert_no = (info.id_no or info.student_no or "").strip()
            self.repo.upsert_id_card_info(
                item_id=item.id,
                name_plain=(info.name or "").strip(),
                id_no_enc=encrypt_text(cert_no) if cert_no else None,
                id_no_last4=cert_no[-4:] if len(cert_no) >= 4 else cert_no or None,
                address_enc=encrypt_text((info.address or "").strip()) if (info.address or "").strip() else None,
                source=info.source or "manual",
            )
        feature_indexed = False
        feature_note = ""
        try:
            from app.services.clip_service import ClipService

            feature_indexed = ClipService.refresh_item_features(self.repo.db, item.id)
            if not feature_indexed:
                feature_note = "特征写入失败，可稍后执行回填脚本"
        except Exception as exc:
            logging.getLogger(__name__).warning("refresh feature after create failed item_id=%s: %s", item.id, exc)
            feature_note = "特征写入异常，可稍后执行回填脚本"
        return {
            "id": item.id,
            "title": item.title,
            "item_type": item.item_type,
            "feature_indexed": feature_indexed,
            "feature_note": feature_note,
        }

    def list_items(self, item_type: int | None, status: int, page: int, page_size: int, keyword: str | None = None, item_type_id: int | None = None):
        items, total = self.repo.list_items(item_type, status, page, page_size, keyword=keyword, item_type_id=item_type_id)
        result = []
        for item in items:
            imgs = self.repo.get_item_images(item.id)
            result.append({
                "id": item.id,
                "item_type": item.item_type,
                "item_type_id": item.item_type_id,
                "title": item.title,
                "cover_image": imgs[0].image_url if imgs else "",
                "location_name": item.location_detail or "",
                "lost_found_time": str(item.lost_found_time) if item.lost_found_time else "",
                "status": item.status,
                "status_label": self._status_label(item.item_type, item.status),
                "is_id_card_match": bool(item.item_type_id == 9 and (keyword or "").strip()),
                "created_at": str(item.created_at),
            })
        return {"list": result, "total": total, "page": page, "page_size": page_size}

    def get_item_detail(self, item_id: int):
        item = self.repo.get_item(item_id)
        if not item:
            return None
        imgs = self.repo.get_item_images(item.id)
        return {
            "id": item.id,
            "user_id": item.user_id,
            "item_type": item.item_type,
            "title": item.title,
            "description": item.description,
            "status": item.status,
            "status_label": self._status_label(item.item_type, item.status),
            "location_detail": item.location_detail,
            "lost_found_time": str(item.lost_found_time) if item.lost_found_time else "",
            "contact_info": item.contact_info,
            "images": [{"id": img.id, "url": img.image_url} for img in imgs],
            "expires_at": str(item.expires_at) if item.expires_at else "",
            "closed_at": str(item.closed_at) if item.closed_at else "",
            "created_at": str(item.created_at),
        }

    def my_items(self, user_id: int, page: int, page_size: int, item_type: int | None = None):
        rows, total = self.repo.list_by_user(user_id, page, page_size, item_type=item_type)
        return {
            "list": [
                {
                    "id": item.id,
                    "item_type": item.item_type,
                    "title": item.title,
                    "status": item.status,
                    "status_label": self._status_label(item.item_type, item.status),
                    "created_at": str(item.created_at),
                }
                for item in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def update_status(self, user_id: int, item_id: int, status: int):
        item = self.repo.get_item(item_id)
        if not item:
            return None, "物品不存在"
        if item.user_id != user_id:
            return None, "仅发布者可修改状态"
        if status not in (1, 2, 3):
            return None, "状态无效"
        item.status = status
        if status == 3:
            item.closed_at = datetime.now()
        if status == 1:
            item.closed_at = None
        self.repo.save(item)
        return {
            "id": item.id,
            "status": item.status,
            "status_label": self._status_label(item.item_type, item.status),
        }, None
