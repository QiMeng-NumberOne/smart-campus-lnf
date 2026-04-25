import json
import time
import urllib.parse
import urllib.request

from app.config import settings
from app.models.user import User


class WechatSubscribeService:
    _token_cache: str | None = None
    _token_expire_at: float = 0.0

    @classmethod
    def _get_access_token(cls) -> str | None:
        now = time.time()
        if cls._token_cache and now < cls._token_expire_at - 60:
            return cls._token_cache
        if not settings.wechat_appid or not settings.wechat_secret:
            return None
        q = urllib.parse.urlencode(
            {
                "grant_type": "client_credential",
                "appid": settings.wechat_appid,
                "secret": settings.wechat_secret,
            }
        )
        url = f"https://api.weixin.qq.com/cgi-bin/token?{q}"
        try:
            with urllib.request.urlopen(url, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception:
            return None
        token = data.get("access_token")
        if not token:
            return None
        cls._token_cache = token
        cls._token_expire_at = now + int(data.get("expires_in", 7200))
        return token

    @classmethod
    def send_match_notification(cls, user: User, target_item_id: int, similarity: float) -> bool:
        if not user or not user.wechat_openid or not user.match_notification_enabled:
            return False
        template_id = settings.wechat_subscribe_match_template_id
        if not template_id:
            return False
        token = cls._get_access_token()
        if not token:
            return False
        url = f"https://api.weixin.qq.com/cgi-bin/message/subscribe/send?access_token={token}"
        page = f"pages/item-detail/item-detail?id={target_item_id}"
        payload = {
            "touser": user.wechat_openid,
            "template_id": template_id,
            "page": page,
            "data": {
                "thing1": {"value": "失物招领高相似匹配"},
                "thing2": {"value": "检测到可能是您要找的物品"},
                "number3": {"value": round(similarity * 100, 1)},
            },
            "lang": "zh_CN",
        }
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url=url, data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return int(data.get("errcode", -1)) == 0
        except Exception:
            return False
