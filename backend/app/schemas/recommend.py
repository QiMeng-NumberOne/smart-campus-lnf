from pydantic import BaseModel, Field


class RecommendEventCreate(BaseModel):
    item_id: int = Field(..., ge=1)
    behavior_type: str = Field(
        ...,
        description="view | click_detail | favorite | click_contact | comment | search",
    )
