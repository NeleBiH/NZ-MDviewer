"""
Settings manager — standalone functions, no Qt imports at module level.
"""
import os
import json

SETTINGS_FILE = os.path.expanduser("~/.local/share/nzmdviewer/settings.json")

_DEFAULTS: dict = {
    "language": "en",
    "auto_hide_sidebar": False,
    "sidebar_visible": True,
    "sidebar_width": 250,
    "remember_sidebar_pos": True,
    "auto_refresh": True,
    "default_zoom": 1.0,
    "default_editor": "xdg-open",
    "recent_files": [],
}


def ucitaj_postavke() -> dict:
    """Učitava postavke iz JSON fajla; vraća dict sa default vrijednostima za sve."""
    postavke = dict(_DEFAULTS)
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            postavke.update(saved)
            # Ensure recent_files is always a list
            if not isinstance(postavke.get("recent_files"), list):
                postavke["recent_files"] = []
    except Exception as e:
        print(f"Greška pri učitavanju postavki: {e}")
    return postavke


def sacuvaj_postavke(postavke: dict) -> None:
    """Čuva postavke u JSON fajl."""
    try:
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(postavke, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Greška pri čuvanju postavki: {e}")
