from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=200)
    reply_to_comment_id: int | None = None
    reply_to_username: str | None = None
