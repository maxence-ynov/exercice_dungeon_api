import asyncio
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.models.player import Player
from app.schemas.hero import HeroCreate, HeroRead, MoveRequest, RoomRead, CombatRead, RestRead
from app.services.auth import current_player
from app.services import game

router = APIRouter(prefix="/heroes", tags=["Héros"])


@router.post("", status_code=201, response_model=HeroRead)
def create(payload: HeroCreate, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.create_hero(session, player, payload)


@router.get("", response_model=list[HeroRead])
def list_all(session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.list_heroes(session, player)


@router.get("/{hero_id}", response_model=HeroRead)
def get_one(hero_id: int, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.read_hero(game.owned_hero(session, hero_id, player))


@router.get("/{hero_id}/room", response_model=RoomRead)
def room(hero_id: int, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.room_description(game.owned_hero(session, hero_id, player))


@router.post("/{hero_id}/move", response_model=RoomRead)
def move(hero_id: int, payload: MoveRequest, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.move(session, game.owned_hero(session, hero_id, player), payload.direction)


@router.post("/{hero_id}/attack", response_model=CombatRead)
def attack(hero_id: int, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    return game.attack(session, game.owned_hero(session, hero_id, player))


@router.post("/{hero_id}/rest", response_model=RestRead)
async def rest(hero_id: int, session: Session = Depends(get_session), player: Player = Depends(current_player)):
    hero = game.owned_hero(session, hero_id, player)
    game.assert_alive(hero)
    game.assert_not_fighting(hero)
    await asyncio.sleep(3)
    game.rest_finish(session, hero)
    return RestRead(message="Le héros a récupéré tous ses points de vie.", pv_heros=hero.pv, pv_max=hero.pv_max)
