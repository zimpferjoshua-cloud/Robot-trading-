"""
Stockage simple des signaux générés, en JSON.
Suffisant pour un usage personnel. L'app mobile (artifact) lira ce fichier
pour afficher les signaux.
"""

import json
import os
from datetime import datetime, timezone

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def save_current_signals(signals: list[dict]):
    """
    Écrase le fichier des signaux courants avec l'état le plus récent.
    Chaque signal est un dict : {ticker, action, prix, raison, indicateurs, horodatage}
    """
    _ensure_data_dir()
    payload = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
    }
    with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def append_to_history(signals: list[dict]):
    """
    Ajoute les signaux du jour à l'historique, pour pouvoir analyser
    la performance des signaux passés plus tard.
    """
    _ensure_data_dir()
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "signals": signals,
    })

    # Garde seulement les 500 derniers relevés pour ne pas grossir indéfiniment
    history = history[-500:]

    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_current_signals() -> dict:
    if not os.path.exists(SIGNALS_FILE):
        return {"updated_at": None, "signals": []}
    with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)
