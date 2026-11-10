from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.schemas.auth import RegisterRequest, PlayerRead, TokenRead
from app.services import auth as service

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=PlayerRead, status_code=201)
def register(payload: RegisterRequest, session: Session = Depends(get_session)):
    return service.register(session, payload)


@router.post("/login", response_model=TokenRead)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    return service.login(session, form.username, form.password)
