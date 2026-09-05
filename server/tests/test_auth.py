def test_login_returns_token(client):
    resp = client.post("/api/auth/wechat", json={"code": "test_code"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["token"]
    assert body["user_id"] > 0
    # session_key 绝不能返回前端
    assert "session_key" not in body


def test_login_creates_same_user(client):
    r1 = client.post("/api/auth/wechat", json={"code": "c1"})
    r2 = client.post("/api/auth/wechat", json={"code": "c2"})
    assert r1.json()["user_id"] == r2.json()["user_id"]


def test_protected_requires_auth(client):
    resp = client.get("/api/spaces")
    assert resp.status_code == 401


def test_invalid_token_rejected(client):
    resp = client.get("/api/spaces", headers={"Authorization": "Bearer invalid"})
    assert resp.status_code == 401
