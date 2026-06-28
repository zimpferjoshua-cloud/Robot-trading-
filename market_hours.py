"""
Vérifie si la bourse américaine (NYSE/NASDAQ) est ouverte.
Les actions listées dans watchlist.py sont toutes des actions US,
qui se tradent de 9h30 à 16h00, heure de New York, du lundi au vendredi
(hors jours fériés américains — non gérés ici par simplicité, à ajouter
avec la librairie `pandas_market_calendars` si besoin de précision totale).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

NY_TZ = ZoneInfo("America/New_York")


def is_market_open() -> bool:
    now_ny = datetime.now(NY_TZ)

    # Marché fermé le week-end
    if now_ny.weekday() >= 5:  # 5 = samedi, 6 = dimanche
        return False

    market_open = now_ny.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now_ny.replace(hour=16, minute=0, second=0, microsecond=0)

    return market_open <= now_ny <= market_close


def next_market_status_message() -> str:
    if is_market_open():
        return "Le marché est actuellement ouvert."
    now_ny = datetime.now(NY_TZ)
    if now_ny.weekday() >= 5:
        return "Le marché est fermé (week-end)."
    return "Le marché est fermé (hors horaires 9h30-16h00, heure de New York)."
