from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_space_membership, require_event_owner
from app.models import User
from app.schemas.event import EventCreate, EventOut, EventUpdate
from app.services import event_service

router = APIRouter(tags=["events"])


@router.get("/api/spaces/{space_id}/events", response_model=list[EventOut])
def list_events(
    space_id: int,
    day: str | None = Query(default=None, description="YYYY-MM-DD，按东八区当天"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[EventOut]:
    get_space_membership(space_id, current_user.id, db)
    query_start = None
    query_end = None
    if day:
        query_start, query_end = event_service.day_range_utc(day)
    return event_service.list_events(db, space_id, query_start, query_end)


@router.post("/api/events", response_model=EventOut, status_code=201)
def create_event(
    payload: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventOut:
    get_space_membership(payload.space_id, current_user.id, db)
    return event_service.create_event(db, current_user.id, payload)


@router.patch("/api/events/{event_id}", response_model=EventOut)
def update_event(
    event_id: int,
    payload: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> EventOut:
    event = event_service.get_event(db, event_id)
    member = get_space_membership(event.space_id, current_user.id, db)
    require_event_owner(member, event.user_id, current_user.id)
    return event_service.update_event(db, event, payload)


@router.delete("/api/events/{event_id}", status_code=204)
def delete_event(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    event = event_service.get_event(db, event_id)
    member = get_space_membership(event.space_id, current_user.id, db)
    require_event_owner(member, event.user_id, current_user.id)
    event_service.delete_event(db, event)
