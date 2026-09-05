def _make_space_and_get_cards(client, headers):
    space = client.post(
        "/api/spaces", json={"name": "测试", "type": "custom"}, headers=headers
    ).json()
    cards = client.get(
        f"/api/spaces/{space['id']}/cards", headers=headers
    ).json()
    return space, cards


def test_create_and_update_card(client, auth_headers):
    space, _ = _make_space_and_get_cards(client, auth_headers)
    resp = client.post(
        f"/api/spaces/{space['id']}/cards",
        json={"name": "喝水", "icon": "💧", "type": "point"},
        headers=auth_headers,
    )
    assert resp.status_code == 201
    card = resp.json()
    assert card["name"] == "喝水"

    patch = client.patch(
        f"/api/cards/{card['id']}",
        json={"name": "喝水2"},
        headers=auth_headers,
    )
    assert patch.status_code == 200
    assert patch.json()["name"] == "喝水2"


def test_delete_card_soft(client, auth_headers):
    space, _ = _make_space_and_get_cards(client, auth_headers)
    card = client.post(
        f"/api/spaces/{space['id']}/cards",
        json={"name": "待删", "type": "point"},
        headers=auth_headers,
    ).json()

    resp = client.delete(f"/api/cards/{card['id']}", headers=auth_headers)
    assert resp.status_code == 204

    # 删除后列表不再包含
    cards = client.get(
        f"/api/spaces/{space['id']}/cards", headers=auth_headers
    ).json()
    assert all(c["id"] != card["id"] for c in cards)


def test_non_admin_cannot_create_card(client, auth_headers):
    space, _ = _make_space_and_get_cards(client, auth_headers)

    from app.database import TestingSessionLocal
    from app.models import User, SpaceMember
    from app.security import create_access_token
    from app.models.space_member import ROLE_MEMBER

    db = TestingSessionLocal()
    user = User(openid="test_openid_003")
    db.add(user)
    db.commit()
    db.refresh(user)
    user_id = user.id
    db.add(SpaceMember(space_id=space["id"], user_id=user_id, role=ROLE_MEMBER))
    db.commit()
    db.close()

    token_member = create_access_token(user_id)
    headers_member = {"Authorization": f"Bearer {token_member}"}

    resp = client.post(
        f"/api/spaces/{space['id']}/cards",
        json={"name": "越权卡", "type": "point"},
        headers=headers_member,
    )
    assert resp.status_code == 403
