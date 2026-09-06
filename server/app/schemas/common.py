"""统一的 UTC 时间处理。

数据库统一存 UTC 的 naive datetime（MySQL DATETIME 本就不带时区）。
对外序列化时必须带上 UTC 时区标记（Z / +00:00），否则前端 JS 会把
naive 时间当成本地时间解析，导致中国用户出现 8 小时时差。
"""
from datetime import datetime, timezone
from typing import Annotated, Any

from pydantic import PlainSerializer


def ensure_utc(dt: datetime) -> datetime:
    """将 naive datetime 视为 UTC，并附加 tzinfo（已是 aware 则原样返回）。"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _serialize_utc(dt: datetime) -> str:
    """序列化为带时区标记的 ISO 8601（如 2026-09-05T07:30:00Z）。"""
    dt = ensure_utc(dt)
    # 统一转成 UTC 再输出，避免出现 +08:00 之类
    dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


# 用于 Out schema 的 datetime 字段：读入时补 UTC，输出时带 Z
UtcDateTime = Annotated[
    datetime,
    PlainSerializer(_serialize_utc, return_type=str, when_used="json"),
]
