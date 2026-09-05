from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Card
from app.schemas.card import CardCreate, CardUpdate


def list_cards(db: Session, space_id: int) -> list[Card]:
    return (
        db.query(Card)
        .filter(Card.space_id == space_id, Card.deleted_at.is_(None))
        .order_by(Card.sort_order.asc(), Card.id.asc())
        .all()
    )


def create_card(db: Session, space_id: int, payload: CardCreate) -> Card:
    card = Card(
        space_id=space_id,
        name=payload.name,
        icon=payload.icon,
        type=payload.type,
        sort_order=payload.sort_order,
        config=payload.config,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_card(db: Session, card_id: int) -> Card:
    card = db.get(Card, card_id)
    if card is None or card.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="卡片不存在")
    return card


def update_card(db: Session, card: Card, payload: CardUpdate) -> Card:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(card, key, value)
    db.commit()
    db.refresh(card)
    return card


def delete_card(db: Session, card: Card) -> None:
    """软删除卡片（与 Event 软删除保持一致）。"""
    from app.models.mixins import utcnow

    card.deleted_at = utcnow()
    db.commit()
