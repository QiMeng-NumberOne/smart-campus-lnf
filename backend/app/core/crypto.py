import base64
import hashlib

from cryptography.fernet import Fernet

from app.config import settings


def _build_fernet() -> Fernet:
    raw = (settings.sensitive_encrypt_key or settings.jwt_secret or "smart-campus-lnf").encode("utf-8")
    key = base64.urlsafe_b64encode(hashlib.sha256(raw).digest())
    return Fernet(key)


def encrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return _build_fernet().encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return _build_fernet().decrypt(value.encode("utf-8")).decode("utf-8")
