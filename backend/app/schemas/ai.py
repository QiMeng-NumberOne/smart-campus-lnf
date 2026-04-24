from pydantic import BaseModel


class RecognizeItemRequest(BaseModel):
    image_id: int | None = None
    conf_threshold: float | None = None


class ApplySuggestionRequest(BaseModel):
    item_id: int
    image_id: int | None = None
    item_type_id: int


class RecognizeImageRequest(BaseModel):
    image_url: str
    conf_threshold: float | None = None
