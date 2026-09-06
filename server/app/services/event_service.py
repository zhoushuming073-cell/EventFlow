from datetime import datetime, time, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models import Card, Event
from app.models.card import TYPE_DURATION, TYPE_POINT
from app.models.mixins import utcnow
from app.schemas.event import EventCreate, EventUpdate


def _utc_now() -> datetime:
    return utcnow()


def list_events(
    db: Session,
    space_id: int,
    query_start: datetime | None = None,
    query_end: datetime | None = None,
) -> list[Event]:
    """查询事件。

    当给定 query_start/query_end 时，按「事件时间区间与查询区间重叠」过滤：
      - 事件的 start_at 早于查询区间结束
      - 且 (事件未结束 或 事件 end_at 晚于查询区间开始)
    这样能覆盖跨天事件（如 23:00 开始、次日 07:00 结束的睡觉）。
    """
    q = db.query(Event).filter(
        Event.space_id == space_id, Event.deleted_at.is_(None)
    )
    if query_start is not None and query_end is not None:
        q = q.filter(
            Event.start_at < query_end,
            or_(Event.end_at.is_(None), Event.end_at > query_start),
        )
    return q.order_by(Event.start_at.desc()).all()


def create_event(db: Session, user_id: int, payload: EventCreate) -> Event:
    card = db.get(Card, payload.card_id)
    if card is None or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")
    if card.space_id != payload.space_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="卡片不属于该空间")

    start_at = payload.start_at or _utc_now()
    end_at = payload.end_at

    # point 卡片：立即结束，end_at = start_at
    if card.type == TYPE_POINT:
        end_at = start_at

    # duration 卡片：同一用户在同一 Space 同一时间只能有一个进行中的持续事件。
    # 启动新的持续事件时，自动结束上一个进行中的事件。
    if card.type == TYPE_DURATION and end_at is None:
        ongoing = (
            db.query(Event)
            .filter(
                Event.space_id == payload.space_id,
                Event.user_id == user_id,
                Event.end_at.is_(None),
                Event.deleted_at.is_(None),
            )
            .all()
        )
        for ev in ongoing:
            # 同一张卡重复启动属于误操作，直接返回冲突提示；不同卡则自动结束上一张
            if ev.card_id == card.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="该卡片已有进行中的事件",
                )
            ev.end_at = start_at

    if end_at is not None and end_at < start_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="end_at 不能早于 start_at"
        )

    event = Event(
        space_id=payload.space_id,
        card_id=card.id,
        user_id=user_id,
        start_at=start_at,
        end_at=end_at,
        data=payload.data,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, event_id: int) -> Event:
    event = db.get(Event, event_id)
    if event is None or event.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在")
    return event


def update_event(db: Session, event: Event, payload: EventUpdate) -> Event:
    data = payload.model_dump(exclude_unset=True)

    new_start = data.get("start_at", event.start_at)
    new_end = data.get("end_at", event.end_at)

    # 结束一个进行中的事件：显式传 end_at=null 表示"现在结束"
    if "end_at" in data and data["end_at"] is None:
        if event.end_at is None:
            new_end = _utc_now()
            data["end_at"] = new_end
        else:
            # 已结束的事件不允许被重新打开（清空 end_at）
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已结束的事件不能重新打开",
            )

    if new_end is not None and new_end < new_start:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="end_at 不能早于 start_at"
        )

    for key, value in data.items():
        setattr(event, key, value)
    db.commit()
    db.refresh(event)
    return event


def delete_event(db: Session, event: Event) -> None:
    """软删除事件。"""
    event.deleted_at = _utc_now()
    db.commit()


def day_range_utc(day: str) -> tuple[datetime, datetime]:
    """将 'YYYY-MM-DD'（东八区当天）换算为 UTC 区间 [start, end)。

    返回的 start/end 是 UTC naive datetime，供区间重叠查询使用。
    """
    try:
        d = datetime.strptime(day, "%Y-%m-%d").date()
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="日期格式应为 YYYY-MM-DD") from e

    tz = timezone(timedelta(hours=8))
    start_local = datetime.combine(d, time.min, tzinfo=tz)
    end_local = start_local + timedelta(days=1)
    return (
        start_local.astimezone(timezone.utc).replace(tzinfo=None),
        end_local.astimezone(timezone.utc).replace(tzinfo=None),
    )
