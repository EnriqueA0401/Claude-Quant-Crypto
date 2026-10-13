"""Datos externos (fuera de data.binance.vision), con hash en el manifest."""
from __future__ import annotations

import json

import pandas as pd
import requests

from .data import DATA, _record, sha256

DERIBIT = "https://www.deribit.com/api/v2/public/get_volatility_index_data"


def fetch_dvol(currency: str, start: str = "2021-01-01", end: str = "2026-10-01") -> pd.Series:
    """Índice DVOL diario de Deribit (volatilidad implícita a 30 días, %), close por día UTC.
    Se guarda en data/deribit/dvol_{currency}.json y su hash se registra en el manifest."""
    dest = DATA / "deribit" / f"dvol_{currency}.json"
    if not dest.exists():
        rows, t0 = [], int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
        t_end = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000)
        while t0 < t_end:
            t1 = min(t0 + 900 * 86_400_000, t_end)
            r = requests.get(DERIBIT, params={"currency": currency, "start_timestamp": t0,
                                              "end_timestamp": t1, "resolution": 86400}, timeout=60)
            r.raise_for_status()
            rows += r.json()["result"]["data"]
            t0 = t1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rows))
    blob = dest.read_bytes()
    _record(f"deribit/dvol_{currency}.json", sha256(blob))
    df = pd.DataFrame(json.loads(blob), columns=["ts", "open", "high", "low", "close"])
    s = pd.Series(df["close"].to_numpy(), index=pd.to_datetime(df["ts"], unit="ms", utc=True))
    return s[~s.index.duplicated()].sort_index()
