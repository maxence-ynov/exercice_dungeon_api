from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.models.hero import Hero
from app.schemas.hero import LeaderboardEntry

router = APIRouter(tags=["Classement"])


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(session: Session = Depends(get_session)):
    heroes = session.exec(select(Hero).order_by(Hero.victoire.desc(), Hero.or_.desc(), Hero.id.asc()).limit(10)).all()
    return [LeaderboardEntry(rang=i, nom=hero.nom, classe=hero.classe, or_=hero.or_, victoire=hero.victoire) for i, hero in enumerate(heroes, 1)]
