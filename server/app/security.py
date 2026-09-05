from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from app.config import settings

ALGORITHM = settings.jwt_algorithm


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def create_access_token(user_id: int) -> str:
    """生成 JWT，sub 为用户 id。"""
    expire = _now_utc() + timedelta(minutes=settings.jwt_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "exp": expire,
        "iat": _now_utc(),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """校验 JWT，返回用户 id；无效则返回 None。"""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except JWTError:
        return None
    sub = payload.get("sub")
    if sub is None:
        return None
    try:
        return int(sub)
    except (TypeError, ValueError):
        return None
