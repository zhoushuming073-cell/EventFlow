from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

CardType = Literal["point", "duration"]


class CardCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    icon: str | None = Field(default=None, max_length=16)
    type: CardType = "point"
    sort_order: int = 0
    config: dict = Field(default_factory=dict)


class CardUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    icon: str | None = Field(default=None, max_length=16)
    type: CardType | None = None
    sort_order: int | None = None
    config: dict | None = None


class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    space_id: int
    name: str
    icon: str | None
    type: str
    sort_order: int
    config: dict
    created_at: datetime
    updated_at: datetime
