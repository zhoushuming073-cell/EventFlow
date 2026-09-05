import secrets

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.auth import WeChatLoginIn
from app.security import create_access_token
from app.wechat import WeChatError, code2session


async def login_wechat(db: Session, payload: WeChatLoginIn) -> tuple[str, int]:
    """微信登录：code 换 openid，查询或创建用户，返回 (token, user_id)。"""
    try:
        wx_data = await code2session(payload.code)
    except WeChatError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"微信登录失败：{e.errmsg}",
        ) from e

    openid = wx_data["openid"]
    user = db.query(User).filter(User.openid == openid).first()
    if user is None:
        user = User(openid=openid)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 可选更新昵称/头像
    changed = False
    if payload.nickname and payload.nickname != user.nickname:
        user.nickname = payload.nickname
        changed = True
    if payload.avatar_url and payload.avatar_url != user.avatar_url:
        user.avatar_url = payload.avatar_url
        changed = True
    if changed:
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return token, user.id


def generate_invite_code() -> str:
    """生成 8 位安全随机邀请码。"""
    return secrets.token_hex(4)
