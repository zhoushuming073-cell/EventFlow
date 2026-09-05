from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import TokenOut, WeChatLoginIn
from app.services.auth_service import login_wechat

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/wechat", response_model=TokenOut)
async def wechat_login(payload: WeChatLoginIn, db: Session = Depends(get_db)) -> TokenOut:
    token, user_id = await login_wechat(db, payload)
    return TokenOut(token=token, user_id=user_id)
