from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, get_space_membership, require_admin
from app.models import User
from app.schemas.card import CardCreate, CardOut, CardUpdate
from app.services import card_service

router = APIRouter(tags=["cards"])


@router.get("/api/spaces/{space_id}/cards", response_model=list[CardOut])
def list_cards(
    space_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[CardOut]:
    get_space_membership(space_id, current_user.id, db)
    return card_service.list_cards(db, space_id)


@router.post("/api/spaces/{space_id}/cards", response_model=CardOut, status_code=201)
def create_card(
    space_id: int,
    payload: CardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CardOut:
    member = get_space_membership(space_id, current_user.id, db)
    require_admin(member)
    return card_service.create_card(db, space_id, payload)


@router.patch("/api/cards/{card_id}", response_model=CardOut)
def update_card(
    card_id: int,
    payload: CardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CardOut:
    card = card_service.get_card(db, card_id)
    member = get_space_membership(card.space_id, current_user.id, db)
    require_admin(member)
    return card_service.update_card(db, card, payload)


@router.delete("/api/cards/{card_id}", status_code=204)
def delete_card(
    card_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    card = card_service.get_card(db, card_id)
    member = get_space_membership(card.space_id, current_user.id, db)
    require_admin(member)
    card_service.delete_card(db, card)
