"""
Moteur de signaux — le cœur du robot.

Stratégie utilisée (volontairement simple et transparente) :
- Tendance : prix au-dessus de la moyenne mobile 50 jours = tendance haussière
- Déclencheur : croisement de la moyenne mobile 20 jours au-dessus/en-dessous
  de la moyenne mobile 50 jours (golden cross / death cross)
- Filtre de confirmation : RSI pour éviter d'acheter en surachat (>70) ou
  de vendre en survente (<30)
- Filtre de confirmation 2 : histogramme MACD positif/négatif

Cette stratégie NE GARANTIT AUCUN PROFIT. Elle sert de point de départ
raisonnable, transparent et facile à ajuster. Le marché reste imprévisible.

IMPORTANT : ce script ne passe AUCUN ordre réel. Il génère uniquement
des signaux d'observation (ACHAT / VENTE / ATTENTE) à titre informatif.
"""

import time
from datetime import datetime, timezone

import pandas as pd
import yfinance as yf

from watchlist import WATCHLIST
from indicators import sma, rsi, macd, average_true_range
from storage import save_current_signals, append_to_history
from market_hours import is_market_open, next_market_status_message


def fetch_price_history(ticker: str, period: str = "6mo", interval: str = "1d"):
    """Récupère l'historique de prix pour un ticker via Yahoo Finance (gratuit)."""
    try:
        data = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if data is None or data.empty or len(data) < 60:
            return None
        return data
    except Exception as e:
        print(f"[ERREUR] Impossible de récupérer {ticker} : {e}")
        return None


def analyze_ticker(ticker: str):
    """
    Analyse un ticker et retourne un signal structuré.
    """
    data = fetch_price_history(ticker)
    if data is None:
        return None

    close = data["Close"]
    high = data["High"]
    low = data["Low"]

    sma20 = sma(close, 20)
    sma50 = sma(close, 50)
    rsi14 = rsi(close, 14)
    macd_line, signal_line, hist = macd(close)
    atr14 = average_true_range(high, low, close, 14)

    last_close = float(close.iloc[-1])
    last_sma20 = float(sma20.iloc[-1])
    last_sma50 = float(sma50.iloc[-1])
    prev_sma20 = float(sma20.iloc[-2])
    prev_sma50 = float(sma50.iloc[-2])
    last_rsi = float(rsi14.iloc[-1])
    last_hist = float(hist.iloc[-1])
    last_atr = float(atr14.iloc[-1])

    golden_cross = prev_sma20 <= prev_sma50 and last_sma20 > last_sma50
    death_cross = prev_sma20 >= prev_sma50 and last_sma20 < last_sma50
    uptrend = last_close > last_sma50
    downtrend = last_close < last_sma50

    action = "ATTENTE"
    raisons = []

    if golden_cross and last_rsi < 70 and last_hist > 0:
        action = "ACHAT"
        raisons.append("Croisement haussier des moyennes mobiles (20j au-dessus de 50j)")
        raisons.append(f"RSI à {last_rsi:.0f} (pas de surachat)")
        raisons.append("MACD positif (momentum haussier confirmé)")
    elif uptrend and last_rsi < 60 and last_hist > 0 and prev_sma20 < last_sma20:
        action = "ACHAT"
        raisons.append("Tendance haussière confirmée, momentum en accélération")
        raisons.append(f"RSI à {last_rsi:.0f} (marge avant surachat)")

    elif death_cross and last_rsi > 30:
        action = "VENTE"
        raisons.append("Croisement baissier des moyennes mobiles (20j sous 50j)")
        raisons.append(f"RSI à {last_rsi:.0f}")
        raisons.append("MACD négatif (momentum baissier)")
    elif downtrend and last_rsi > 40 and last_hist < 0 and prev_sma20 > last_sma20:
        action = "VENTE"
        raisons.append("Tendance baissière confirmée, momentum en accélération à la baisse")

    if not raisons:
        raisons.append("Aucun signal fort détecté — tendance et momentum ne sont pas alignés")

    stop_loss_suggere = round(last_close - 2 * last_atr, 2) if action == "ACHAT" else None
    take_profit_suggere = round(last_close + 3 * last_atr, 2) if action == "ACHAT" else None

    return {
        "ticker": ticker,
        "action": action,
        "prix": round(last_close, 2),
        "raisons": raisons,
        "indicateurs": {
            "sma20": round(last_sma20, 2),
            "sma50": round(last_sma50, 2),
            "rsi": round(last_rsi, 1),
            "macd_histogramme": round(last_hist, 3),
            "atr": round(last_atr, 2),
        },
        "stop_loss_suggere": stop_loss_suggere,
        "take_profit_suggere": take_profit_suggere,
        "horodatage": datetime.now(timezone.utc).isoformat(),
    }


def run_scan():
    """Scanne toute la watchlist et retourne la liste des signaux."""
    resultats = []
    for ticker in WATCHLIST:
        signal = analyze_ticker(ticker)
        if signal:
            resultats.append(signal)
        time.sleep(0.5)
    return resultats


def run_once():
    """Exécute un scan complet et sauvegarde les résultats."""
    print(f"[{datetime.now()}] Lancement du scan sur {len(WATCHLIST)} actions...")
    signaux = run_scan()

    achats = [s for s in signaux if s["action"] == "ACHAT"]
    ventes = [s for s in signaux if s["action"] == "VENTE"]

    print(f"  -> {len(achats)} signal(aux) d'achat, {len(ventes)} signal(aux) de vente")

    save_current_signals(signaux)
    append_to_history(signaux)
    return signaux


if __name__ == "__main__":
    run_once()
