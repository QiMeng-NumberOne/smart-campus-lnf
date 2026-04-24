from pydantic import BaseModel
from typing import Optional
from app.schemas.id_card import IdCardInfoIn


class ItemImageIn(BaseModel):
    url: str


class ItemCreate(BaseModel):
    item_type: int
    item_type_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    location_id: Optional[int] = None
    location_detail: Optional[str] = None
    lost_found_time: Optional[str] = None
    contact_info: Optional[str] = None
    images: list[ItemImageIn] = []
    id_card_info: Optional[IdCardInfoIn] = None


class ItemStatusUpdate(BaseModel):
    status: int
