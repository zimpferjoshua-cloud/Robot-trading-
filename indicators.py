"""
Calcul des indicateurs techniques utilisés par le moteur de signaux.
Aucune dépendance externe type ta-lib : tout est recalculé à la main avec pandas,
pour rester simple à installer (juste pandas et numpy).
"""

import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """Moyenne mobile simple."""
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Moyenne mobile exponentielle."""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Relative Strength Index (RSI).
    Oscille entre 0 et 100. Au-dessus de 70 = surachat, en dessous de 30 = survente.
    """
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_value = 100 - (100 / (1 + rs))
    return rsi_value.fillna(50)  # valeur neutre si pas assez de données


def macd(series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
    """
    MACD (Moving Average Convergence Divergence).
    Retourne (ligne_macd, ligne_signal, histogramme).
    """
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """
    ATR : mesure de la volatilité, utile pour fixer un stop-loss adapté à chaque action.
    """
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()
