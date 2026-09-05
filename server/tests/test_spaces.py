from app.database import TestingSessionLocal
from app.models import User
from app.security import create_access_token


def _create_second_user_token() -> str:
    db = TestingSessionLocal()
    user = User(openid="test_openid_002")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    return create_access_token(user.id)


def test_create_space_with_baby_template(client, auth_headers):
    resp = client.post(
        "/api/spaces",
        json={"name": "宝宝", "type": "baby"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "宝宝"
    assert body["role"] == "owner"
    assert body["invite_code"]

    space_id = body["id"]
    cards = client.get(
        f"/api/spaces/{space_id}/cards", headers=auth_headers
    ).json()
    assert len(cards) == 5
    names = {c["name"] for c in cards}
    assert names == {"喝奶", "睡觉", "换尿布", "辅食", "洗澡"}


def test_list_spaces(client, auth_headers):
    client.post("/api/spaces", json={"name": "s1", "type": "custom"}, headers=auth_headers)
    client.post("/api/spaces", json={"name": "s2", "type": "study"}, headers=auth_headers)
    spaces = client.get("/api/spaces", headers=auth_headers).json()
    assert len(spaces) == 2


def test_cannot_access_other_user_space(client, auth_headers):
    # 用户 A 创建空间
    space = client.post(
        "/api/spaces", json={"name": "A的空间", "type": "custom"}, headers=auth_headers
    ).json()
    space_id = space["id"]

    # 用户 B 的 token
    token_b = _create_second_user_token()
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 用户 B 无权访问 A 的空间
    resp = client.get(f"/api/spaces/{space_id}", headers=headers_b)
    assert resp.status_code == 403

    resp = client.get(f"/api/spaces/{space_id}/cards", headers=headers_b)
    assert resp.status_code == 403
