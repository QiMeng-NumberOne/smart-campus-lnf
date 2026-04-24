import json

from app.repositories.message_repository import MessageRepository


class MessageService:
    def __init__(self, repo: MessageRepository):
        self.repo = repo

    def list_messages(self, user_id: int, page: int, page_size: int):
        rows, total = self.repo.list_for_user(user_id, page, page_size)
        def normalize_content(raw: str):
            if raw.startswith("[评论JSON]"):
                body = raw.replace("[评论JSON]", "", 1)
                try:
                    data = json.loads(body)
                    text = data.get("text", "")
                    reply_to = data.get("reply_to_username")
                    return {
                        "text": text,
                        "kind": "comment",
                        "reply_to_username": reply_to,
                    }
                except Exception:
                    return {"text": body, "kind": "comment", "reply_to_username": None}
            if raw.startswith("[评论]"):
                return {"text": raw.replace("[评论]", "", 1), "kind": "comment", "reply_to_username": None}
            return {"text": raw, "kind": "system", "reply_to_username": None}

        return {
            "list": [
                (
                    lambda payload: {
                        "id": row.id,
                        "item_id": row.item_id,
                        "content": payload["text"],
                        "kind": payload["kind"],
                        "reply_to_username": payload["reply_to_username"],
                        "is_read": bool(row.is_read),
                        "created_at": str(row.created_at),
                    }
                )(normalize_content(row.content))
                for row in rows
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
        }

    def unread_count(self, user_id: int):
        return {"count": self.repo.unread_count(user_id)}

    def mark_read(self, user_id: int, message_id: int):
        return self.repo.mark_read(user_id, message_id)
