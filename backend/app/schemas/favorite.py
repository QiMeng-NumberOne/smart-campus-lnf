from pydantic import BaseModel


class FavoriteCreate(BaseModel):
    item_id: int
