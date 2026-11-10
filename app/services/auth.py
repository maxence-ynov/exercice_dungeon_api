"""Inscription, mot de passe Argon2, JWT et contrôle du compte courant."""
from datetime import datetime, timedelta, timezone
import os

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.database import get_session
from app.models.player import Player
from app.schemas.auth import RegisterRequest
from app.services.errors import fail

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-only-change-this-secret-before-deployment")
ALGORITHM = "HS256"
TOKEN_MINUTES = 60
password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def register(session: Session, payload: RegisterRequest) -> Player:
    if session.exec(select(Player).where(Player.username == payload.username)).first():
        fail(409, "USERNAME_TAKEN", "Ce nom d'utilisateur est déjà utilisé.")
    player = Player(username=payload.username, password_hash=password_hash.hash(payload.password))
    session.add(player)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        fail(409, "USERNAME_TAKEN", "Ce nom d'utilisateur est déjà utilisé.")
    session.refresh(player)
    return player


def login(session: Session, username: str, password: str) -> dict:
    player = session.exec(select(Player).where(Player.username == username)).first()
    if player is None or not password_hash.verify(password, player.password_hash):
        fail(401, "BAD_CREDENTIALS", "Identifiants incorrects.")
    exp = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_MINUTES)
    return {"access_token": jwt.encode({"sub": str(player.id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM), "token_type": "bearer"}


def current_player(token: str | None = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> Player:
    if not token:
        fail(401, "UNAUTHORIZED", "Authentification requise.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["sub", "exp"]})
        player_id = int(payload["sub"])
    except (jwt.PyJWTError, ValueError, TypeError, KeyError):
        fail(401, "UNAUTHORIZED", "Token invalide ou expiré.")
    player = session.get(Player, player_id)
    if player is None:
        fail(401, "UNAUTHORIZED", "Compte introuvable.")
    return player
