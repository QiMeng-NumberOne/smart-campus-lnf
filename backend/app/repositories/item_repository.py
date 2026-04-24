from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.models.item import Item, ItemImage
from app.models.id_card_info import IdCardInfo


class ItemRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_item(self, item: Item) -> Item:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def add_images(self, images: list[ItemImage]) -> None:
        for image in images:
            self.db.add(image)
        self.db.commit()

    def list_items(self, item_type: int | None, status: int, page: int, page_size: int, keyword: str | None = None, item_type_id: int | None = None):
        now = datetime.now()
        q = self.db.query(Item).filter(
            Item.status == status,
            Item.is_deleted == 0,
            or_(Item.expires_at == None, Item.expires_at >= now),
        )
        if item_type:
            q = q.filter(Item.item_type == item_type)
        if item_type_id:
            q = q.filter(Item.item_type_id == item_type_id)
        if keyword:
            kw = f"%{keyword.strip()}%"
            # 仅在证件筛选时才按姓名匹配，避免其它分类被证件姓名“串搜”
            if item_type_id == 9:
                q = q.outerjoin(IdCardInfo, IdCardInfo.item_id == Item.id).filter(
                    or_(
                        Item.title.like(kw),
                        Item.description.like(kw),
                        Item.location_detail.like(kw),
                        IdCardInfo.name_plain.like(kw),
                    )
                )
            else:
                q = q.filter(
                    or_(
                        Item.title.like(kw),
                        Item.description.like(kw),
                        Item.location_detail.like(kw),
                    )
                )
        total = q.count()
        items = q.order_by(Item.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def get_item(self, item_id: int) -> Item | None:
        return self.db.query(Item).filter(Item.id == item_id).first()

    def get_item_images(self, item_id: int) -> list[ItemImage]:
        return self.db.query(ItemImage).filter(ItemImage.item_id == item_id).order_by(ItemImage.sort_order).all()

    def list_by_user(self, user_id: int, page: int, page_size: int, item_type: int | None = None):
        q = self.db.query(Item).filter(Item.user_id == user_id, Item.is_deleted == 0)
        if item_type:
            q = q.filter(Item.item_type == item_type)
        total = q.count()
        items = q.order_by(Item.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def save(self, item: Item) -> Item:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def upsert_id_card_info(self, item_id: int, name_plain: str, id_no_enc: str | None, id_no_last4: str | None, address_enc: str | None, source: str = "manual"):
        row = self.db.query(IdCardInfo).filter(IdCardInfo.item_id == item_id).first()
        if not row:
            row = IdCardInfo(item_id=item_id)
        row.name_plain = name_plain
        row.id_no_enc = id_no_enc
        row.id_no_last4 = id_no_last4
        row.address_enc = address_enc
        row.source = source
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
