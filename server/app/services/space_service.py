from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Card, Space, SpaceMember
from app.models.space_member import ROLE_OWNER
from app.schemas.space import SpaceCreate
from app.services.auth_service import generate_invite_code
from app.services.templates import TEMPLATE_CARDS


def list_spaces(db: Session, user_id: int) -> list[dict]:
    """列出当前用户加入的所有空间，附带用户角色。"""
    rows = (
        db.query(Space, SpaceMember.role)
        .join(SpaceMember, SpaceMember.space_id == Space.id)
        .filter(SpaceMember.user_id == user_id)
        .order_by(Space.id.desc())
        .all()
    )
    result: list[dict] = []
    for space, role in rows:
        item = {
            "id": space.id,
            "name": space.name,
            "type": space.type,
            "owner_id": space.owner_id,
            "invite_code": space.invite_code,
            "created_at": space.created_at,
            "role": role,
        }
        result.append(item)
    return result


def create_space(db: Session, user_id: int, payload: SpaceCreate) -> Space:
    """创建 Space，owner 自动成为成员，并按模板预置卡片。"""
    space = Space(
        name=payload.name,
        type=payload.type,
        owner_id=user_id,
        invite_code=generate_invite_code(),
    )
    db.add(space)
    db.flush()  # 拿到 space.id

    member = SpaceMember(space_id=space.id, user_id=user_id, role=ROLE_OWNER)
    db.add(member)

    # 按模板预置卡片
    for idx, card_spec in enumerate(TEMPLATE_CARDS.get(payload.type, [])):
        db.add(
            Card(
                space_id=space.id,
                name=card_spec["name"],
                icon=card_spec["icon"],
                type=card_spec["type"],
                sort_order=idx,
            )
        )

    db.commit()
    db.refresh(space)
    return space


def get_space(db: Session, space_id: int) -> Space:
    space = db.get(Space, space_id)
    if space is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="空间不存在")
    return space
