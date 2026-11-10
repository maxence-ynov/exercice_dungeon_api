"""Client terminal : python client/play.py --help"""
import argparse
import json
import os
from pathlib import Path

import requests

API_URL = os.getenv("DUNGEON_API_URL", "http://127.0.0.1:8000").rstrip("/")
TOKEN_PATH = Path(__file__).resolve().parents[1] / ".token"


def main():
    parser = argparse.ArgumentParser(description="Dungeon as a Service — client terminal")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health")
    register = commands.add_parser("register")
    login = commands.add_parser("login")
    for sub in (register, login):
        sub.add_argument("--username", required=True)
        sub.add_argument("--password", required=True)
    create = commands.add_parser("create")
    create.add_argument("--name", required=True)
    create.add_argument("--classe", required=True, choices=["guerrier", "mage", "voleur"])
    for stat in ("force", "agilite", "intelligence"):
        create.add_argument("--" + stat, type=int, required=True)
    for command in ("look", "move", "attack", "rest"):
        sub = commands.add_parser(command)
        sub.add_argument("--hero", type=int, required=True)
        if command == "move":
            sub.add_argument("--direction", choices=["nord", "sud", "est", "ouest"], required=True)
    commands.add_parser("heroes")
    commands.add_parser("leaderboard")
    args = parser.parse_args()
    cmd = args.command
    headers = {}
    if TOKEN_PATH.exists():
        headers["Authorization"] = "Bearer " + TOKEN_PATH.read_text(encoding="utf-8").strip()
    method, path, kwargs = "GET", "/health", {}
    if cmd in ("register", "login"):
        method, path = "POST", "/auth/" + cmd
        kwargs = {"data" if cmd == "login" else "json": {"username": args.username, "password": args.password}}
    elif cmd == "create":
        method, path = "POST", "/heroes"
        kwargs = {"json": {"nom": args.name, "classe": args.classe, "force": args.force, "agilite": args.agilite, "intelligence": args.intelligence}}
    elif cmd == "heroes":
        path = "/heroes"
    elif cmd == "leaderboard":
        path = "/leaderboard"
    elif cmd == "look":
        path = f"/heroes/{args.hero}/room"
    elif cmd in ("move", "attack", "rest"):
        method, path = "POST", f"/heroes/{args.hero}/{cmd}"
        if cmd == "move":
            kwargs = {"json": {"direction": args.direction}}
    try:
        result = requests.request(method, API_URL + path, headers=headers, timeout=15, **kwargs)
        print(f"HTTP {result.status_code}")
        print(json.dumps(result.json(), indent=2, ensure_ascii=False))
        if cmd == "login" and result.ok:
            TOKEN_PATH.write_text(result.json()["access_token"], encoding="utf-8")
            try:
                TOKEN_PATH.chmod(0o600)
            except OSError:
                pass
            print("Token enregistré dans .token")
        result.raise_for_status()
    except requests.RequestException as exc:
        parser.exit(1, f"Erreur réseau ou HTTP : {exc}\n")


if __name__ == "__main__":
    main()
