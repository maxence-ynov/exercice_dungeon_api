"""Orchestration entre carte, entités métier et persistance."""
import logging
from sqlmodel import Session, select

from app.domain.heroes import creer_heros
from app.models.hero import Hero
from app.models.player import Player
from app.schemas.hero import HeroCreate, HeroRead, MonsterRead, RoomRead, CombatRead
from app.services.dungeon_map import START_ROOM, FINAL_ROOM, get_room, get_monster_of_room
from app.services.errors import fail

log = logging.getLogger(__name__)


def read_hero(hero: Hero) -> HeroRead:
    return HeroRead.model_validate({**hero.model_dump(), "en_combat": hero.monstre_pv is not None, "est_vivant": hero.pv > 0})


def owned_hero(session: Session, hero_id: int, player: Player) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        fail(404, "HERO_NOT_FOUND", "Héros introuvable.")
    if hero.owner_id != player.id:
        fail(403, "NOT_YOUR_HERO", "Ce héros appartient à un autre joueur.")
    return hero


def assert_alive(hero: Hero) -> None:
    if hero.pv <= 0:
        fail(409, "HERO_DEAD", "Ce héros est mort.")


def assert_not_fighting(hero: Hero) -> None:
    if hero.monstre_pv is not None:
        fail(409, "IN_COMBAT", "Un combat est en cours.")


def create_hero(session: Session, player: Player, data: HeroCreate) -> HeroRead:
    unit = creer_heros(data.classe, data.force, data.agilite, data.intelligence)
    hero = Hero(**data.model_dump(), pv=unit.pv_max, pv_max=unit.pv_max, salle_actuelle=START_ROOM, owner_id=player.id)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return read_hero(hero)


def list_heroes(session: Session, player: Player) -> list[HeroRead]:
    return [read_hero(x) for x in session.exec(select(Hero).where(Hero.owner_id == player.id).order_by(Hero.id)).all()]


def room_description(hero: Hero) -> RoomRead:
    room = get_room(hero.salle_actuelle)
    monster_info = get_monster_of_room(hero.salle_actuelle) if hero.monstre_pv is not None else None
    monster = (MonsterRead(nom=monster_info["name"], pv=hero.monstre_pv, pv_max=monster_info["hp"], attaque=monster_info["attack"], or_=monster_info["gold"]) if monster_info else None)
    return RoomRead(id=hero.salle_actuelle, nom=room["name"], description=room["description"], sorties=room["exits"], monstre=monster)


def move(session: Session, hero: Hero, direction: str) -> RoomRead:
    assert_alive(hero)
    assert_not_fighting(hero)
    target = get_room(hero.salle_actuelle)["exits"].get(direction)
    if target is None:
        fail(400, "NO_EXIT", f"Il n'y a pas de passage vers le {direction}.")
    hero.salle_actuelle = target
    monster = get_monster_of_room(target)
    hero.monstre_pv = monster["hp"] if monster else None
    session.add(hero)
    session.commit()
    session.refresh(hero)
    log.info("hero=%s move=%s room=%s", hero.id, direction, hero.salle_actuelle)
    return room_description(hero)


def attack(session: Session, hero: Hero) -> CombatRead:
    assert_alive(hero)
    if hero.monstre_pv is None:
        fail(409, "NO_MONSTER", "Aucun monstre à combattre.")
    monster = get_monster_of_room(hero.salle_actuelle)
    unit = creer_heros(hero.classe, hero.force, hero.agilite, hero.intelligence)
    damage, critical = unit.calculer_degats()
    hero.monstre_pv = max(0, hero.monstre_pv - damage)
    damage_taken = 0
    gold = 0
    issue = "en_cours"
    if hero.monstre_pv == 0:
        issue = "monstre_vaincu"
        gold = monster["gold"]
        hero.or_ += gold
        hero.monstre_pv = None
        if hero.salle_actuelle == FINAL_ROOM:
            hero.victoire = True
    else:
        damage_taken = min(hero.pv, unit.subir_degats(monster["attack"]))
        hero.pv = max(0, hero.pv - damage_taken)
        if hero.pv == 0:
            issue = "heros_mort"
    session.add(hero)
    session.commit()
    session.refresh(hero)
    log.info("hero=%s attack=%s critical=%s retaliate=%s result=%s", hero.id, damage, critical, damage_taken, issue)
    return CombatRead(degats_infliges=damage, critique=critical, degats_subis=damage_taken, pv_heros=hero.pv, pv_monstre=hero.monstre_pv or 0, issue=issue, or_gagne=gold, victoire=hero.victoire)


def rest_finish(session: Session, hero: Hero) -> None:
    # Revalidation après la pause, car une autre requête peut avoir changé l'état.
    session.refresh(hero)
    assert_alive(hero)
    assert_not_fighting(hero)
    hero.pv = hero.pv_max
    session.add(hero)
    session.commit()
    session.refresh(hero)
