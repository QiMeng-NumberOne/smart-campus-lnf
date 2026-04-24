from typing import Any


def ok(data: Any = None, message: str = "success") -> dict:
    return {"code": 0, "message": message, "data": data}


def fail(message: str, code: int = 40000, data: Any = None) -> dict:
    return {"code": code, "message": message, "data": data}
