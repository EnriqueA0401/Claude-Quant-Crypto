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


COINMETRICS = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"


def fetch_coinmetrics(asset: str, metrics: list[str], start: str = "2019-01-01",
                      end: str = "2025-10-01") -> pd.DataFrame:
    """Métricas diarias on-chain (Coin Metrics community). AVISO G1: no son datos
    point-in-time (los flujos a exchanges se revisan a posteriori; 'status-time' de 2026
    para valores de 2024), así que un backtest con ellos puede tener sesgo de anticipación.
    """
    name = f"coinmetrics/{asset}_{'_'.join(sorted(metrics))}.json"
    dest = DATA / name
    if not dest.exists():
        rows, url = [], COINMETRICS
        params = {"assets": asset, "metrics": ",".join(metrics), "frequency": "1d",
                  "start_time": start, "end_time": end, "page_size": 10000}
        while url:
            r = requests.get(url, params=params, timeout=60)
            r.raise_for_status()
            j = r.json()
            rows += j["data"]
            url, params = j.get("next_page_url"), None
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rows))
    blob = dest.read_bytes()
    _record(name, sha256(blob))
    df = pd.DataFrame(json.loads(blob))
    df.index = pd.to_datetime(df.pop("time"), utc=True)
    keep = [m for m in metrics if m in df]
    return df[keep].astype(float)


BINANCE_CMS = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"


def fetch_binance_announcements(catalog_id: int) -> pd.DataFrame:
    """Anuncios públicos de Binance (catalogId 161 = deslistados, 48 = listados).
    releaseDate en ms UTC. Se guardan con hash en el manifest."""
    name = f"binance/announcements_{catalog_id}.json"
    dest = DATA / name
    if not dest.exists():
        rows, page = [], 1
        while True:
            r = requests.get(BINANCE_CMS, params={"type": 1, "catalogId": catalog_id,
                                                  "pageNo": page, "pageSize": 50}, timeout=60)
            r.raise_for_status()
            cats = r.json()["data"]["catalogs"]
            arts = cats[0]["articles"] if cats else []
            if not arts:
                break
            rows += [{"releaseDate": a["releaseDate"], "title": a["title"]} for a in arts]
            page += 1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rows))
    blob = dest.read_bytes()
    _record(name, sha256(blob))
    df = pd.DataFrame(json.loads(blob))
    df["ts"] = pd.to_datetime(df["releaseDate"], unit="ms", utc=True)
    return df.sort_values("ts").reset_index(drop=True)


def fetch_stablecoin_supply() -> pd.Series:
    """Oferta total de stablecoins ligadas al USD (DefiLlama), diaria, con hash."""
    name = "defillama/stablecoins_all.json"
    dest = DATA / name
    if not dest.exists():
        r = requests.get("https://stablecoins.llama.fi/stablecoincharts/all", timeout=60)
        r.raise_for_status()
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(r.text)
    blob = dest.read_bytes()
    _record(name, sha256(blob))
    rows = json.loads(blob)
    s = pd.Series({pd.Timestamp(int(x["date"]), unit="s", tz="UTC"):
                   x["totalCirculatingUSD"].get("peggedUSD", float("nan")) for x in rows})
    return s.sort_index().astype(float)


def fetch_hyperliquid_funding(coin: str, start: str = "2023-01-01",
                              end: str = "2025-10-01") -> pd.Series:
    """Funding horario de Hyperliquid (API pública), con hash en el manifest."""
    name = f"hyperliquid/funding_{coin}.json"
    dest = DATA / name
    if not dest.exists():
        rows, t0 = [], int(pd.Timestamp(start, tz="UTC").timestamp() * 1000)
        t_end = int(pd.Timestamp(end, tz="UTC").timestamp() * 1000)
        while t0 < t_end:
            r = requests.post("https://api.hyperliquid.xyz/info", timeout=60,
                              json={"type": "fundingHistory", "coin": coin, "startTime": t0})
            r.raise_for_status()
            page = r.json()
            if not page:
                break
            rows += page
            nxt = page[-1]["time"] + 1
            if nxt <= t0:
                break
            t0 = nxt
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rows))
    blob = dest.read_bytes()
    _record(name, sha256(blob))
    rows = json.loads(blob)
    s = pd.Series({pd.Timestamp(int(x["time"]), unit="ms", tz="UTC"): float(x["fundingRate"])
                   for x in rows})
    return s[~s.index.duplicated()].sort_index()
