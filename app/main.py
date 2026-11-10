"""API Dungeon as a Service — lancement : fastapi dev app/main.py"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from app.database import create_db_and_tables
from app.models.hero import Hero  # noqa: F401 — enregistre la table SQLModel
from app.models.player import Player  # noqa: F401 — enregistre la table SQLModel
from app.routes import auth, heroes, leaderboard

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(application: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="Dungeon as a Service", description="Moteur de jeu de rôle textuel — Pixel Crypt", version="1.0.0", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(heroes.router)
app.include_router(leaderboard.router)


class HealthRead(BaseModel):
    status: str
    message: str


@app.get("/health", response_model=HealthRead, tags=["Système"])
def health():
    return {"status": "ok", "message": "Le donjon vous attend..."}
