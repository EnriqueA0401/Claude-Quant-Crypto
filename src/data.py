"""Carga y validación de datos de data.binance.vision (G1).

Formato kline CSV (sin cabecera en la mayoría de ficheros): open_time, open, high, low,
close, volume, close_time, quote_volume, trades, taker_buy_base, taker_buy_quote, ignore.
Desde 2025-01-01 los ficheros SPOT usan microsegundos en vez de milisegundos.
"""
from __future__ import annotations

import hashlib
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
MANIFEST = ROOT / "data_manifest.json"
BASE_URL = "https://data.binance.vision/data"

KLINE_COLS = ["open_time", "open", "high", "low", "close", "volume", "close_time",
              "quote_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"]


def _to_utc(ts: pd.Series) -> pd.DatetimeIndex:
    v = ts.astype("int64").to_numpy()
    # ms ~1e12-1e13; us ~1e15-1e16
    ns = np.where(v > 10**14, v * 1_000, v * 1_000_000)
    return pd.DatetimeIndex(pd.to_datetime(ns, unit="ns", utc=True))


def parse_klines(raw: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), header=None)
    if not str(df.iloc[0, 0]).lstrip("-").isdigit():  # cabecera presente
        df = df.iloc[1:]
    df.columns = KLINE_COLS
    df["open_time"] = _to_utc(df["open_time"].astype("int64"))
    df["close_time"] = _to_utc(df["close_time"].astype("int64"))
    for c in ["open", "high", "low", "close", "volume", "quote_volume",
              "taker_buy_base", "taker_buy_quote"]:
        df[c] = df[c].astype(float)
    df["trades"] = df["trades"].astype("int64")
    return df.drop(columns="ignore").set_index("open_time").sort_index()


def validate_bars(df: pd.DataFrame, freq: str) -> dict:
    """Informe G1: duplicados, huecos, OHLC incoherentes, precios no positivos."""
    idx = df.index
    full = pd.date_range(idx.min(), idx.max(), freq=freq, tz="UTC")
    missing = full.difference(idx)
    bad_ohlc = ((df["high"] < df[["open", "close"]].max(axis=1)) |
                (df["low"] > df[["open", "close"]].min(axis=1))).sum()
    return {
        "rows": len(df),
        "duplicates": int(idx.duplicated().sum()),
        "missing_bars": len(missing),
        "first_missing": [str(x) for x in missing[:5]],
        "bad_ohlc": int(bad_ohlc),
        "non_positive": int((df[["open", "high", "low", "close"]] <= 0).any(axis=1).sum()),
        "monotonic": bool(idx.is_monotonic_increasing),
    }


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(rel_path: str) -> bytes:
    """Descarga (o lee de caché) un zip de data.binance.vision y registra su hash."""
    dest = DATA / rel_path
    if dest.exists():
        blob = dest.read_bytes()
    else:
        r = requests.get(f"{BASE_URL}/{rel_path}", timeout=60)
        r.raise_for_status()
        blob = r.content
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)
    _record(rel_path, sha256(blob))
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        return z.read(z.namelist()[0])


def _record(rel_path: str, digest: str) -> None:
    man = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    if man.get(rel_path) not in (None, digest):
        raise RuntimeError(f"hash distinto para {rel_path}: datos cambiaron")
    if man.get(rel_path) != digest:
        man[rel_path] = digest
        MANIFEST.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")


def _read_zip(path: Path) -> bytes:
    with zipfile.ZipFile(path) as z:
        return z.read(z.namelist()[0])


def load_klines(market: str, symbol: str, interval: str = "1h",
                kind: str = "klines") -> pd.DataFrame:
    """market: 'spot' o 'um'; kind: 'klines' o 'markPriceKlines' (solo um).
    Concatena los zips mensuales ya descargados."""
    sub = "spot" if market == "spot" else "futures/um"
    # mensuales primero; los diarios rellenan huecos de los mensuales
    files = (sorted((DATA / sub / "monthly" / kind / symbol / interval).glob("*.zip"))
             + sorted((DATA / sub / "daily" / kind / symbol / interval).glob("*.zip")))
    if not files:
        raise FileNotFoundError(f"sin datos {market} {symbol} {interval}")
    df = pd.concat([parse_klines(_read_zip(f)) for f in files])
    return df[~df.index.duplicated(keep="first")].sort_index()


def load_funding(symbol: str) -> pd.Series:
    """Tasa de funding por evento (USDT-M), indexada por hora de liquidación.

    calc_time trae a veces milisegundos de desfase (08:00:00.003); se redondea al
    minuto para que el funding de las 08:00 lo pague la posición mantenida hasta
    las 08:00 (bar 07:00 en el backtester: intervalo (open[t], open[t+1]]).
    """
    files = sorted((DATA / "futures/um/monthly/fundingRate" / symbol).glob("*.zip"))
    if not files:
        raise FileNotFoundError(f"sin funding {symbol}")
    df = pd.concat([pd.read_csv(io.BytesIO(_read_zip(f))) for f in files])
    ts = pd.to_datetime(df["calc_time"].astype("int64"), unit="ms", utc=True).dt.round("1min")
    s = pd.Series(df["last_funding_rate"].astype(float).values, index=ts, name="funding")
    return s[~s.index.duplicated(keep="first")].sort_index()
