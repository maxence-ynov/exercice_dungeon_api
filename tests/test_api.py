from unittest.mock import patch

from tests.conftest import auth_user, create_hero


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_auth_and_hero_creation(client):
    h = auth_user(client)
    result = create_hero(client, h)
    assert result.status_code == 201
    hero = result.json()
    assert hero["pv"] == hero["pv_max"] == 32
    assert hero["salle_actuelle"] == "entree"
    assert "monstre_pv" not in hero and "owner_id" not in hero
    assert hero["en_combat"] is False and hero["est_vivant"] is True
    assert len(client.get("/heroes", headers=h).json()) == 1


def test_invalid_creation(client):
    h = auth_user(client)
    cases = [
        {"nom": "x"}, {"nom": "x" * 21}, {"classe": "paladin"},
        {"force": 0}, {"agilite": 9}, {"intelligence": 2.5},
        {"force": 8, "agilite": 5, "intelligence": 2},
        {"force": True},
    ]
    for data in cases:
        assert create_hero(client, h, **data).status_code == 422


def test_missing_hero_and_protection(client):
    a = auth_user(client)
    hero_id = create_hero(client, a).json()["id"]
    assert client.get("/heroes/9999", headers=a).json()["detail"]["error"] == "HERO_NOT_FOUND"
    assert client.get("/heroes").status_code == 401
    assert client.get("/heroes", headers={"Authorization": "Bearer invalid"}).status_code == 401
    b = auth_user(client, "bob")
    assert client.get("/heroes", headers=b).json() == []
    result = client.post(f"/heroes/{hero_id}/move", json={"direction": "nord"}, headers=b)
    assert result.status_code == 403 and result.json()["detail"]["error"] == "NOT_YOUR_HERO"


def test_move_and_bad_exit(client):
    h = auth_user(client)
    hero_id = create_hero(client, h).json()["id"]
    bad = client.post(f"/heroes/{hero_id}/move", json={"direction": "ouest"}, headers=h)
    assert bad.status_code == 400 and bad.json()["detail"]["error"] == "NO_EXIT"
    assert client.post(f"/heroes/{hero_id}/move", json={"direction": "up"}, headers=h).status_code == 422
    result = client.post(f"/heroes/{hero_id}/move", json={"direction": "nord"}, headers=h)
    assert result.status_code == 200 and result.json()["id"] == "hall"
    assert client.get(f"/heroes/{hero_id}", headers=h).json()["salle_actuelle"] == "hall"


def test_combat_and_gold(client):
    h = auth_user(client)
    hero_id = create_hero(client, h).json()["id"]
    attack = lambda: client.post(f"/heroes/{hero_id}/attack", headers=h)
    assert attack().json()["detail"]["error"] == "NO_MONSTER"
    client.post(f"/heroes/{hero_id}/move", json={"direction": "nord"}, headers=h)
    room = client.post(f"/heroes/{hero_id}/move", json={"direction": "ouest"}, headers=h).json()
    assert room["monstre"]["pv"] == 12
    blocked = client.post(f"/heroes/{hero_id}/move", json={"direction": "est"}, headers=h)
    assert blocked.status_code == 409 and blocked.json()["detail"]["error"] == "IN_COMBAT"
    hit = attack()
    assert hit.status_code == 200
    assert hit.json()["issue"] == "monstre_vaincu"
    assert hit.json()["or_gagne"] == 10
    assert hit.json()["degats_subis"] == 0
    assert client.get(f"/heroes/{hero_id}", headers=h).json()["or_"] == 10
    assert client.get(f"/heroes/{hero_id}/room", headers=h).json()["monstre"] is None


def test_rest_and_dead_hero(client):
    h = auth_user(client)
    hero_id = create_hero(client, h, classe="mage", force=2, agilite=2, intelligence=6).json()["id"]
    client.post(f"/heroes/{hero_id}/move", json={"direction": "nord"}, headers=h)
    client.post(f"/heroes/{hero_id}/move", json={"direction": "ouest"}, headers=h)
    assert client.post(f"/heroes/{hero_id}/rest", headers=h).json()["detail"]["error"] == "IN_COMBAT"
    # Réduit les PV pour tester le repos et le traitement de la mort.
    from app.database import engine
    from app.models.hero import Hero
    from sqlmodel import Session
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        hero.monstre_pv = None
        hero.pv = 1
        session.add(hero)
        session.commit()
    with patch("app.routes.heroes.asyncio.sleep") as mock_sleep:
        result = client.post(f"/heroes/{hero_id}/rest", headers=h)
    mock_sleep.assert_awaited_once_with(3)
    assert result.status_code == 200 and result.json()["pv_heros"] == 24
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        hero.pv = 0
        session.add(hero)
        session.commit()
    for action in ("rest", "attack", "move"):
        response = client.post(f"/heroes/{hero_id}/{action}", headers=h, json={"direction": "sud"} if action == "move" else None)
        assert response.status_code == 409 and response.json()["detail"]["error"] == "HERO_DEAD"
    assert client.get(f"/heroes/{hero_id}", headers=h).json()["est_vivant"] is False


def test_liche_victory_and_leaderboard(client):
    h = auth_user(client)
    hero_id = create_hero(client, h).json()["id"]
    from app.database import engine
    from app.models.hero import Hero
    from sqlmodel import Session
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        hero.salle_actuelle = "salle_trone"
        hero.monstre_pv = 8
        session.add(hero)
        session.commit()
    response = client.post(f"/heroes/{hero_id}/attack", headers=h)
    assert response.json()["victoire"] is True
    assert response.json()["or_gagne"] == 100
    assert client.get("/leaderboard").json()[0]["victoire"] is True


def test_password_is_hashed_and_duplicates(client):
    from sqlmodel import Session, select
    from app.database import engine
    from app.models.player import Player
    assert client.post("/auth/register", json={"username": "alice", "password": "strongpass123"}).status_code == 201
    assert client.post("/auth/register", json={"username": "alice", "password": "strongpass123"}).status_code == 409
    with Session(engine) as session:
        player = session.exec(select(Player).where(Player.username == "alice")).one()
        assert player.password_hash != "strongpass123"
        assert player.password_hash.startswith("$argon2")
    assert client.post("/auth/login", data={"username": "alice", "password": "wrongpassword"}).status_code == 401
