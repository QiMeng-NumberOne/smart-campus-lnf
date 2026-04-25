from app.core.media_url import normalize_media_url
from app.repositories.favorite_repository import FavoriteRepository
from app.repositories.item_repository import ItemRepository
from app.services.recommend_service import RecommendService


class FavoriteService:
    def __init__(self, favorite_repo: FavoriteRepository, item_repo: ItemRepository):
        self.favorite_repo = favorite_repo
        self.item_repo = item_repo

    def add(self, user_id: int, item_id: int):
        exists = self.favorite_repo.get_one(user_id, item_id)
        if not exists:
            self.favorite_repo.create(user_id, item_id)
            try:
                RecommendService(self.favorite_repo.db).log_behavior(user_id, item_id, "favorite")
            except Exception:
                pass
        return True

    def remove(self, user_id: int, item_id: int):
        row = self.favorite_repo.get_one(user_id, item_id)
        if row:
            self.favorite_repo.delete(row)
        return True

    def list(self, user_id: int):
        item_ids = self.favorite_repo.list_ids(user_id)
        data = []
        for item_id in item_ids:
            item = self.item_repo.get_item(item_id)
            if not item:
                continue
            imgs = self.item_repo.get_item_images(item.id)
            data.append(
                {
                    "id": item.id,
                    "item_type": item.item_type,
                    "title": item.title,
                    "cover_image": normalize_media_url(imgs[0].image_url) if imgs else "",
                    "status": item.status,
                }
            )
        return {"list": data, "total": len(data)}
