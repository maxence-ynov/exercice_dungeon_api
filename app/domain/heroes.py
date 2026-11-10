"""Moteur des combats : POO pure, sans FastAPI ni SQLModel."""
from abc import ABC, abstractmethod
import random


class Heros(ABC):
    def __init__(self, force: int, agilite: int, intelligence: int):
        self.force = force
        self.agilite = agilite
        self.intelligence = intelligence

    @property
    def pv_max(self) -> int:
        return 20 + self.force * 2

    @abstractmethod
    def calculer_degats(self) -> tuple[int, bool]:
        """Retourne (dégâts, coup_critique)."""

    def subir_degats(self, attaque_monstre: int) -> int:
        return max(0, attaque_monstre)


class Guerrier(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 2 + self.force * 2, False

    def subir_degats(self, attaque_monstre: int) -> int:
        return max(1, attaque_monstre - 1)


class Mage(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 1 + self.intelligence * 3, False


class Voleur(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        critique = random.randrange(3) == 0
        return (2 + self.agilite * 2) * (2 if critique else 1), critique


CLASSES = {"guerrier": Guerrier, "mage": Mage, "voleur": Voleur}


def creer_heros(classe: str, force: int, agilite: int, intelligence: int) -> Heros:
    return CLASSES[classe](force, agilite, intelligence)
