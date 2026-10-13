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


def fetch_coinbase_daily(product: str = "BTC-USD", start: str = "2019-12-01",
                         end: str = "2025-10-02") -> pd.Series:
    """Close diario de Coinbase (API pública de candles), con hash en el manifest."""
    name = f"coinbase/{product}_1d.json"
    dest = DATA / name
    if not dest.exists():
        rows, t0, t_end = [], pd.Timestamp(start, tz="UTC"), pd.Timestamp(end, tz="UTC")
        while t0 < t_end:
            t1 = min(t0 + pd.Timedelta("299D"), t_end)
            r = requests.get(f"https://api.exchange.coinbase.com/products/{product}/candles",
                             params={"granularity": 86400, "start": t0.isoformat(),
                                     "end": t1.isoformat()}, timeout=60)
            r.raise_for_status()
            rows += r.json()
            t0 = t1
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(rows))
    blob = dest.read_bytes()
    _record(name, sha256(blob))
    s = pd.Series({pd.Timestamp(int(x[0]), unit="s", tz="UTC"): float(x[4]) for x in json.loads(blob)})
    return s[~s.index.duplicated()].sort_index()


DERIBIT_CHART = "https://www.deribit.com/api/v2/public/get_tradingview_chart_data"


def deribit_quarterly_names(currency: str, start: str = "2018-01", end: str = "2026-09") -> list[str]:
    """Nombres de los trimestrales de Deribit (último viernes de mar/jun/sep/dic)."""
    out = []
    for m in pd.period_range(start, end, freq="M"):
        if m.month not in (3, 6, 9, 12):
            continue
        d = pd.Timestamp(m.end_time.date())
        while d.dayofweek != 4:
            d -= pd.Timedelta("1D")
        out.append(f"{currency}-{d.day}{d.strftime('%b').upper()}{d.strftime('%y')}")
    return out


def fetch_deribit_future_daily(name: str) -> pd.DataFrame | None:
    """Velas diarias de un futuro de Deribit (también vencidos), con hash en el manifest."""
    path = f"deribit/futures/{name}.json"
    dest = DATA / path
    if not dest.exists():
        exp_guess = pd.Timestamp.now(tz="UTC")
        r = requests.get(DERIBIT_CHART, params={"instrument_name": name, "resolution": "1D",
                                                "start_timestamp": 1483228800000,
                                                "end_timestamp": int(exp_guess.timestamp() * 1000)},
                         timeout=60)
        if r.status_code != 200 or "result" not in r.json():
            return None
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(r.json()["result"]))
    blob = dest.read_bytes()
    _record(path, sha256(blob))
    j = json.loads(blob)
    if not j.get("ticks"):
        return None
    df = pd.DataFrame({"open": j["open"], "high": j["high"], "close": j["close"],
                       "volume": j["volume"]},
                      index=pd.to_datetime(j["ticks"], unit="ms", utc=True))
    return df[df["volume"] > 0]
