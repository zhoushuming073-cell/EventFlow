from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    openid: str
    nickname: str | None
    avatar_url: str | None
    created_at: datetime
