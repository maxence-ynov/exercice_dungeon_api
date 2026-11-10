from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class HeroCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nom: str = Field(min_length=3, max_length=20)
    classe: Literal["guerrier", "mage", "voleur"]
    force: int = Field(ge=1, le=8, strict=True)
    agilite: int = Field(ge=1, le=8, strict=True)
    intelligence: int = Field(ge=1, le=8, strict=True)

    @model_validator(mode="after")
    def validate_points(self):
        if self.force + self.agilite + self.intelligence != 10:
            raise ValueError("La somme des statistiques doit être exactement 10.")
        return self


class HeroRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nom: str
    classe: str
    force: int
    agilite: int
    intelligence: int
    pv: int
    pv_max: int
    salle_actuelle: str
    or_: int
    victoire: bool
    en_combat: bool
    est_vivant: bool


class MoveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    direction: Literal["nord", "sud", "est", "ouest"]


class MonsterRead(BaseModel):
    nom: str
    pv: int
    pv_max: int
    attaque: int
    or_: int


class RoomRead(BaseModel):
    id: str
    nom: str
    description: str
    sorties: dict[str, str]
    monstre: MonsterRead | None


class CombatRead(BaseModel):
    degats_infliges: int
    critique: bool
    degats_subis: int
    pv_heros: int
    pv_monstre: int
    issue: Literal["en_cours", "monstre_vaincu", "heros_mort"]
    or_gagne: int
    victoire: bool


class RestRead(BaseModel):
    message: str
    pv_heros: int
    pv_max: int


class LeaderboardEntry(BaseModel):
    rang: int
    nom: str
    classe: str
    or_: int
    victoire: bool
