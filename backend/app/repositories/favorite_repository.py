from sqlalchemy.orm import Session

from app.models.favorite import UserFavorite


class FavoriteRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_one(self, user_id: int, item_id: int) -> UserFavorite | None:
        return self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id, UserFavorite.item_id == item_id).first()

    def create(self, user_id: int, item_id: int) -> UserFavorite:
        favorite = UserFavorite(user_id=user_id, item_id=item_id)
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def delete(self, favorite: UserFavorite) -> None:
        self.db.delete(favorite)
        self.db.commit()

    def list_ids(self, user_id: int) -> list[int]:
        rows = self.db.query(UserFavorite).filter(UserFavorite.user_id == user_id).all()
        return [row.item_id for row in rows]
