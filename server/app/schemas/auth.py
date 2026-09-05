from pydantic import BaseModel


class WeChatLoginIn(BaseModel):
    code: str
    nickname: str | None = None
    avatar_url: str | None = None


class TokenOut(BaseModel):
    token: str
    user_id: int
