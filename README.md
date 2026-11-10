# Dungeon as a Service

Projet réalisé dans le cadre du module **Python Backend & FastAPI**.

L'objectif est de développer une API REST permettant de jouer à un petit jeu de rôle depuis un terminal. Le joueur peut créer un héros, explorer un donjon, combattre des monstres et tenter de vaincre la Liche.

Le projet utilise **Python, FastAPI, Pydantic, SQLModel et SQLite**, avec une authentification par JWT.

## Installation et lancement

Python 3.10 minimum.

Depuis le dossier du projet, exécuter :

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

L'API est ensuite accessible sur :

http://127.0.0.1:8000/docs

Cette page permet de tester les différentes routes directement avec Swagger.

## Fonctionnalités réalisées

Les quatre paliers du sujet ont été implémentés :

- **Palier 1 — Héros :** création, validation des statistiques et consultation des héros.
- **Palier 2 — Donjon :** sauvegarde des données en SQLite, exploration des salles et déplacements.
- **Palier 3 — Combat :** système de combat avec trois classes (Guerrier, Mage et Voleur), gestion des dégâts, de l'or et du repos.
- **Palier 4 — Sécurité :** création de comptes, connexion JWT et protection des héros selon leur propriétaire.

Les règles du jeu sont séparées des routes API afin de garder un code organisé et facile à maintenir.

## Bonus réalisés

- Client permettant de jouer depuis le terminal (`client/play.py`).
- Classement des 10 meilleurs héros (`GET /leaderboard`).
- Tests automatisés avec pytest.
- Possibilité d'utiliser PostgreSQL avec Docker.
- Journalisation des déplacements et combats.

## Tests

Pour lancer les tests :

```powershell
python -m pytest -q
```

**Résultat obtenu : 9 tests réussis sur 9.**

L'API démarre correctement et la documentation Swagger est accessible. Un avertissement de nettoyage du fichier SQLite temporaire apparaît toutefois sous Windows après les tests.

## Notre rendu

- **Membres du groupe :** Maxence
- **Dépôt Git :** https://github.com/maxence-ynov/exercice_dungeon_api
- **Palier atteint :** Palier 4 implémenté
- **Bonus :** B-1, B-2, B-3, B-4 et B-5
- **Difficultés rencontrées :** installation initiale des dépendances et problème de suppression d'une base SQLite temporaire après les tests.

