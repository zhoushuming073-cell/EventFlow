from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SpaceType = Literal["baby", "study", "daily", "pet", "custom"]
RoleType = Literal["owner", "admin", "member"]


class SpaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    type: SpaceType = "custom"


class SpaceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    owner_id: int
    invite_code: str
    created_at: datetime
    role: str | None = None  # 当前用户在空间中的角色


class SpaceDetailOut(SpaceOut):
    member_count: int = 0
