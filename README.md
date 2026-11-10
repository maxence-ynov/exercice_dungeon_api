# Dungeon as a Service — Pixel Crypt

API REST pour un mini jeu de rôle terminal. Projet basé sur le squelette fourni (FastAPI, Pydantic, SQLModel, SQLite, JWT). **Les quatre paliers sont implémentés dans le code.**

## Installation

Python 3.10+ requis (recommandé : 3.11+). Depuis la racine du projet :

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
fastapi dev app/main.py
```

Sous macOS/Linux, activez plutôt `source .venv/bin/activate`. La documentation Swagger est accessible à **http://127.0.0.1:8000/docs** ; `GET /health` doit renvoyer `status: ok`. Le fichier `dungeon.db` est créé automatiquement ; il ne doit pas être inclus dans le rendu.

## Démonstration dans Swagger (ordre recommandé)

1. `POST /auth/register` : `{"username":"alice","password":"strongpass123"}`.
2. Cliquez sur **Authorize** dans Swagger : saisissez `alice` et `strongpass123` (OAuth2). Vous pouvez aussi utiliser `POST /auth/login` (formulaire `application/x-www-form-urlencoded`).
3. `POST /heroes` : `{"nom":"Aragorn","classe":"guerrier","force":6,"agilite":2,"intelligence":2}` → **201**, 32 PV, salle `entree`.
4. Recommencez avec les statistiques `8,5,2` → **422**. `GET /heroes/9999` → **404** avec `detail.error`.
5. `POST /heroes/{id}/move` avec `{"direction":"nord"}` → hall. Depuis le hall, `ouest` → bibliothèque et Gobelin (12 PV).
6. `POST /heroes/{id}/attack` → victoire sur le Gobelin, **10 or** avec ce guerrier. En combat, un déplacement donne `409 IN_COMBAT`.
7. `POST /heroes/{id}/rest` hors combat → attend **3 secondes**, restaure tous les PV.
8. Créez un second compte (`bob`), authentifiez-vous avec Bob et tentez de déplacer le héros d'Alice → **403 NOT_YOUR_HERO**. Sans connexion → **401**. `GET /heroes` liste seulement les héros du compte actif.
9. `GET /leaderboard` renvoie le top 10 public (victoire puis or).

## Routes

| Méthode | Chemin | Fonction | Accès |
| --- | --- | --- | --- |
| GET | `/health` | Santé du serveur | Public |
| POST | `/auth/register` | Créer un compte, mot de passe haché | Public |
| POST | `/auth/login` | Authentification OAuth2, jeton JWT | Public |
| POST | `/heroes` | Créer un héros | JWT |
| GET | `/heroes` | Mes héros | JWT |
| GET | `/heroes/{hero_id}` | Détail d'un héros | Propriétaire |
| GET | `/heroes/{hero_id}/room` | Salle et éventuel monstre | Propriétaire |
| POST | `/heroes/{hero_id}/move` | Déplacer le héros | Propriétaire |
| POST | `/heroes/{hero_id}/attack` | Tour de combat | Propriétaire |
| POST | `/heroes/{hero_id}/rest` | Repos asynchrone | Propriétaire |
| GET | `/leaderboard` | Top 10 | Public |

Erreurs métier : `{"detail":{"error":"NO_EXIT","message":"..."}}`. La validation Pydantic fournit automatiquement les erreurs 422.

## Organisation du code

- `app/models/` : tables `Player` et `Hero` (SQLModel).
- `app/schemas/` : validation et contrats des réponses (Pydantic).
- `app/domain/heroes.py` : moteur orienté objet (classe abstraite + Guerrier/Mage/Voleur).
- `app/services/` : logique métier, propriété des héros, JWT, carte du donjon.
- `app/routes/` : routes HTTP et dépendances.
- `client/play.py` : bonus client terminal.
- `tests/` : tests automatisés FastAPI TestClient.
- `openapi.json` : description OpenAPI préparée hors ligne à partir des mêmes routes et schémas. **Pour obtenir l’export officiel exact**, exécuter `python export_openapi.py` après installation des dépendances (ou enregistrer `/openapi.json` depuis le serveur).

Les fichiers fournis `app/database.py`, `app/services/dungeon_map.py` et `data/dungeon_map.json` restent **inchangés**.

## Client terminal (bonus)

```bash
python client/play.py register --username alice --password strongpass123
python client/play.py login --username alice --password strongpass123
python client/play.py create --name Aragorn --classe guerrier --force 6 --agilite 2 --intelligence 2
python client/play.py heroes
python client/play.py look --hero 1
python client/play.py move --hero 1 --direction nord
python client/play.py attack --hero 1
python client/play.py rest --hero 1
python client/play.py leaderboard
```

La connexion sauvegarde un jeton dans `.token` (ignoré par Git). URL personnalisée avec `DUNGEON_API_URL`.

## Tests

```bash
python -m pytest -q
```

Les tests sont conçus pour couvrir notamment 201, 422, 404, 400, 409, 401, 403, une victoire finale, le hachage et le classement. Un rapport de tests réel doit être produit sur une machine ayant installé les dépendances ; ne pas déclarer les tests réussis avant de les avoir exécutés.

## PostgreSQL (bonus)

```bash
docker compose up -d postgres
```

Configurez `DATABASE_URL=postgresql+psycopg://dungeon:dungeon@localhost:5432/dungeon` dans l'environnement du terminal avant de lancer l'API. Aucun changement de code n'est nécessaire. Les identifiants du compose sont destinés au développement local uniquement.

## Sécurité et limites

Le secret JWT est chargé via `JWT_SECRET_KEY` (valeur de secours **strictement locale**). Définissez un secret long et aléatoire avant tout déploiement. Les mots de passe sont hachés via pwdlib/Argon2. Les données ne sont jamais retournées avec le hash ni l'owner_id. Les modifications simultanées du **même héros** ne sont pas sérialisées : pour un usage public multijoueur, ajouter une stratégie transactionnelle de verrouillage/concurrence et des migrations. SQLite reste adapté à la démonstration demandée.

## Notre rendu

- **Membres du groupe :** À renseigner avant dépôt.
- **Lien du dépôt Git :** À renseigner après création du dépôt.
- **Palier atteint :** 4 implémenté, validation réelle à confirmer après exécution sur la machine de rendu.
- **Bonus réalisés dans le code :** B-1 client terminal, B-2 classement, B-3 tests pytest, B-4 configuration PostgreSQL, B-5 logs de déplacement et combat.
- **Ce qui ne fonctionne pas / difficultés :** L'environnement de préparation ne disposait pas de SQLModel / pwdlib et ne permettait pas de télécharger les paquets ; tests API non exécutables ici. Installer les dépendances, lancer `pytest` et `python export_openapi.py` avant remise. Le secret par défaut n'est pas destiné à la production.
- **Fichiers à remettre :** ZIP sans `.venv/` et `dungeon.db`, README, `openapi.json` à la racine.

**Attention :** la note comporte un critère de commits Git réguliers par membre. Un ZIP ne remplace pas le véritable historique du dépôt ; seuls les membres du groupe peuvent créer leurs commits et indiquer le lien réel du dépôt.
