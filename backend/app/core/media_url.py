"""对外返回的图片/静态资源 URL 与当前服务 base_url 对齐，修正历史数据中的旧端口等。"""

import re

from app.config import settings

# 历史开发环境或其它端口写入数据库后，与当前 base_url 不一致时的替换前缀
_LEGACY_PREFIXES: tuple[str, ...] = (
    "http://127.0.0.1:8090",
    "http://localhost:8090",
)

# 任意主机上旧端口 8090 且路径为 /uploads/...（常见于局域网调试地址写库）
_RE_ANY_HOST_8090_UPLOADS = re.compile(r"^https?://[^/]+:8090(/uploads/.+)$", re.I)


def normalize_media_url(url: str | None) -> str:
    if not url or not isinstance(url, str):
        return ""
    u = url.strip()
    if not u:
        return ""
    base = settings.base_url.rstrip("/")
    for old in _LEGACY_PREFIXES:
        if u.startswith(old):
            return base + u[len(old) :]
    m = _RE_ANY_HOST_8090_UPLOADS.match(u)
    if m:
        return base + m.group(1)
    return u
