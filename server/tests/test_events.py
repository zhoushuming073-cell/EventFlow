def _setup(client, headers, template="study"):
    space = client.post(
        "/api/spaces", json={"name": "测试", "type": template}, headers=headers
    ).json()
    cards = client.get(
        f"/api/spaces/{space['id']}/cards", headers=headers
    ).json()
    return space, cards


def test_point_event_auto_end(client, auth_headers):
    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")

    resp = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    ev = resp.json()
    # point 事件创建即结束
    assert ev["end_at"] is not None


def test_duration_event_start_and_end(client, auth_headers):
    space, cards = _setup(client, auth_headers, "study")
    dur_card = next(c for c in cards if c["type"] == "duration")

    start = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": dur_card["id"]},
        headers=auth_headers,
    )
    assert start.status_code == 201
    ev = start.json()
    assert ev["end_at"] is None

    # 同一卡片重复开始进行中事件 → 409
    dup = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": dur_card["id"]},
        headers=auth_headers,
    )
    assert dup.status_code == 409

    # 结束事件（传 end_at: null 表示"现在结束"）
    end = client.patch(
        f"/api/events/{ev['id']}", json={"end_at": None}, headers=auth_headers
    )
    assert end.status_code == 200
    assert end.json()["end_at"] is not None


def test_list_events_with_day(client, auth_headers):
    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")
    client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    )
    events = client.get(
        f"/api/spaces/{space['id']}/events", headers=auth_headers
    ).json()
    assert len(events) == 1


def test_delete_event_soft(client, auth_headers):
    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")
    ev = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    ).json()

    resp = client.delete(f"/api/events/{ev['id']}", headers=auth_headers)
    assert resp.status_code == 204

    events = client.get(
        f"/api/spaces/{space['id']}/events", headers=auth_headers
    ).json()
    assert len(events) == 0


def test_member_cannot_modify_others_event(client, auth_headers):
    from app.database import TestingSessionLocal
    from app.models import SpaceMember, User
    from app.models.space_member import ROLE_MEMBER
    from app.security import create_access_token

    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")

    # owner 创建一条事件
    ev = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    ).json()

    # 另一个用户以 member 身份加入空间
    db = TestingSessionLocal()
    user = User(openid="member_openid")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.add(SpaceMember(space_id=space["id"], user_id=user_id, role=ROLE_MEMBER))
    db.commit()
    db.close()

    member_headers = {"Authorization": f"Bearer {create_access_token(user_id)}"}

    # member 尝试修改 owner 的事件 → 403
    resp = client.patch(
        f"/api/events/{ev['id']}", json={}, headers=member_headers
    )
    assert resp.status_code == 403

    # member 尝试删除 owner 的事件 → 403
    resp = client.delete(f"/api/events/{ev['id']}", headers=member_headers)
    assert resp.status_code == 403


def test_cannot_reopen_finished_event(client, auth_headers):
    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")
    ev = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    ).json()
    assert ev["end_at"] is not None  # point 事件创建即结束

    # 已结束事件不能被重新打开
    resp = client.patch(
        f"/api/events/{ev['id']}", json={"end_at": None}, headers=auth_headers
    )
    assert resp.status_code == 400
