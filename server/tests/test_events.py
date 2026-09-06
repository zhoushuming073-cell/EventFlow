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


def test_start_new_duration_auto_ends_previous(client, auth_headers):
    """启动不同的 duration 卡片时，自动结束上一个进行中的事件。"""
    space, cards = _setup(client, auth_headers, "study")
    dur_cards = [c for c in cards if c["type"] == "duration"]
    assert len(dur_cards) >= 2

    # 启动第一张
    first = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": dur_cards[0]["id"]},
        headers=auth_headers,
    ).json()
    assert first["end_at"] is None

    # 启动第二张（不同卡）
    second = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": dur_cards[1]["id"]},
        headers=auth_headers,
    ).json()
    assert second["end_at"] is None  # 新事件进行中

    # 第一张应被自动结束
    first_after = client.get(
        f"/api/spaces/{space['id']}/events", headers=auth_headers
    ).json()
    ended = next(e for e in first_after if e["id"] == first["id"])
    assert ended["end_at"] is not None


def test_day_query_returns_cross_midnight_event(client, auth_headers):
    """跨天事件（前一天开始、当天结束）应出现在当天查询结果中。"""
    space, cards = _setup(client, auth_headers, "study")
    dur_card = next(c for c in cards if c["type"] == "duration")

    # 直接通过数据库插入一个跨天事件：昨晚 23:00 开始、今天 07:00 结束
    from datetime import datetime, timedelta, timezone
    from app.database import TestingSessionLocal
    from app.models import Event

    tz8 = timezone(timedelta(hours=8))
    today = datetime.now(tz8).date()
    start_utc = datetime.combine(today, datetime.min.time(), tzinfo=tz8) - timedelta(hours=1)  # 昨天 23:00
    end_utc = datetime.combine(today, datetime.min.time(), tzinfo=tz8) + timedelta(hours=7)  # 今天 07:00
    start_naive = start_utc.astimezone(timezone.utc).replace(tzinfo=None)
    end_naive = end_utc.astimezone(timezone.utc).replace(tzinfo=None)

    db = TestingSessionLocal()
    db.add(
        Event(
            space_id=space["id"],
            card_id=dur_card["id"],
            user_id=1,
            start_at=start_naive,
            end_at=end_naive,
            data={},
        )
    )
    db.commit()
    db.close()

    day = today.strftime("%Y-%m-%d")
    events = client.get(
        f"/api/spaces/{space['id']}/events?day={day}", headers=auth_headers
    ).json()
    # 跨天事件应被包含
    assert any(e["card_id"] == dur_card["id"] for e in events)


def test_event_output_has_utc_timezone(client, auth_headers):
    """事件时间输出应带 UTC 时区标记（Z），供前端正确解析。"""
    space, cards = _setup(client, auth_headers, "baby")
    point_card = next(c for c in cards if c["type"] == "point")
    ev = client.post(
        "/api/events",
        json={"space_id": space["id"], "card_id": point_card["id"]},
        headers=auth_headers,
    ).json()
    # 输出应是带 Z 或 +00:00 的 ISO 时间
    assert ev["start_at"].endswith("Z") or "+00:00" in ev["start_at"]
    assert ev["end_at"].endswith("Z") or "+00:00" in ev["end_at"]
