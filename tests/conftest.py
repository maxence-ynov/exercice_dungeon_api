import os
import tempfile
from pathlib import Path

# Définir la DB AVANT d'importer app.main (engine instancié à l'import).
DB_DIR = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(DB_DIR.name) / "test.db")
os.environ["JWT_SECRET_KEY"] = "test-secret-for-pytest-only"

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from app.database import engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def auth_user(client, name="alice"):
    client.post("/auth/register", json={"username": name, "password": "strongpass123"}).raise_for_status()
    res = client.post("/auth/login", data={"username": name, "password": "strongpass123"})
    assert res.status_code == 200, res.text
    return {"Authorization": "Bearer " + res.json()["access_token"]}


def create_hero(client, headers, **overrides):
    data = {"nom": "Aragorn", "classe": "guerrier", "force": 6, "agilite": 2, "intelligence": 2}
    data.update(overrides)
    return client.post("/heroes", headers=headers, json=data)
