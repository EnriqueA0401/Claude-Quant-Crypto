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
