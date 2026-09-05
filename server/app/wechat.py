from typing import Any

import httpx

from app.config import settings

WECHAT_CODE2SESSION_URL = "https://api.weixin.qq.com/sns/jscode2session"


class WeChatError(Exception):
    """微信接口调用失败。"""

    def __init__(self, errcode: int, errmsg: str) -> None:
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"wechat error {errcode}: {errmsg}")


async def code2session(code: str) -> dict[str, Any]:
    """调用微信 code2Session，返回 openid 等（不含 session_key 给前端）。

    session_key 只在服务端内部使用，绝不能返回给前端。
    """
    if settings.wechat_mock_openid:
        # 本地开发/测试：跳过真实微信调用
        return {"openid": settings.wechat_mock_openid}

    params = {
        "appid": settings.wechat_app_id,
        "secret": settings.wechat_app_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(WECHAT_CODE2SESSION_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

    if "errcode" in data and data["errcode"] != 0:
        raise WeChatError(data["errcode"], data.get("errmsg", "unknown"))

    openid = data.get("openid")
    if not openid:
        raise WeChatError(-1, "no openid returned")

    return data
