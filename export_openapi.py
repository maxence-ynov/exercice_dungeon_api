"""Exporter le schéma reelement genere par l'application, après installation des dépendance."""
import json
from pathlib import Path
from app.main import app

path = Path(__file__).resolve().parent / "openapi.json"
path.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"OpenAPI exporté vers {path}")
