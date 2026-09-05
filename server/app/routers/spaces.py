from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_space_membership
from app.models import SpaceMember, User
from app.schemas.space import SpaceCreate, SpaceDetailOut, SpaceOut
from app.services import space_service

router = APIRouter(prefix="/api/spaces", tags=["spaces"])


@router.get("", response_model=list[SpaceOut])
def list_spaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[SpaceOut]:
    return space_service.list_spaces(db, current_user.id)


@router.post("", response_model=SpaceOut, status_code=201)
def create_space(
    payload: SpaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpaceOut:
    space = space_service.create_space(db, current_user.id, payload)
    return {
        "id": space.id,
        "name": space.name,
        "type": space.type,
        "owner_id": space.owner_id,
        "invite_code": space.invite_code,
        "created_at": space.created_at,
        "role": "owner",
    }


@router.get("/{space_id}", response_model=SpaceDetailOut)
def get_space(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SpaceDetailOut:
    member = get_space_membership(space_id, current_user.id, db)
    space = space_service.get_space(db, space_id)
    member_count = (
        db.query(SpaceMember).filter(SpaceMember.space_id == space_id).count()
    )
    return {
        "id": space.id,
        "name": space.name,
        "type": space.type,
        "owner_id": space.owner_id,
        "invite_code": space.invite_code,
        "created_at": space.created_at,
        "role": member.role,
        "member_count": member_count,
    }
