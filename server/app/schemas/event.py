from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class EventCreate(BaseModel):
    space_id: int
    card_id: int
    start_at: datetime | None = None
    end_at: datetime | None = None
    data: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def check_time_order(self) -> "EventCreate":
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("end_at 必须晚于 start_at")
        return self


class EventUpdate(BaseModel):
    start_at: datetime | None = None
    end_at: datetime | None = None
    data: dict | None = None

    @model_validator(mode="after")
    def check_time_order(self) -> "EventUpdate":
        # 仅当两者都被显式给出时做交叉校验，单边更新由 service 层补全后再校验
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValueError("end_at 必须晚于 start_at")
        return self


class EventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    space_id: int
    card_id: int
    user_id: int
    start_at: datetime
    end_at: datetime | None
    data: dict
    created_at: datetime
    updated_at: datetime
