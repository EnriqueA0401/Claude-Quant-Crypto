"""Universo completo de data.binance.vision (incluye pares deslistados) vía listado S3.

Uso: python3 -m src.universe   (lista perps USDT-M y descarga klines 1d + funding)
"""
from __future__ import annotations

import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

from .data import DATA
from .download import download

S3 = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"


def s3_list(prefix: str, delimiter: str | None = "/") -> tuple[list[str], list[str]]:
    """Devuelve (subprefijos, claves) bajo `prefix`, siguiendo la paginación."""
    prefixes, keys, marker = [], [], ""
    s = requests.Session()
    while True:
        params = {"prefix": prefix, "marker": marker}
        if delimiter:
            params["delimiter"] = delimiter
        for attempt in range(5):
            try:
                r = s.get(S3, params=params, timeout=60)
                r.raise_for_status()
                break
            except requests.RequestException:
                if attempt == 4:
                    raise
                time.sleep(2 ** attempt)
        x = r.text
        prefixes += re.findall(r"<CommonPrefixes><Prefix>([^<]+)</Prefix>", x)
        keys += re.findall(r"<Key>([^<]+)</Key>", x)
        if "<IsTruncated>true</IsTruncated>" not in x:
            return prefixes, keys
        nm = re.search(r"<NextMarker>([^<]+)</NextMarker>", x)
        marker = nm.group(1) if nm else (keys[-1] if keys else prefixes[-1])


def um_usdt_symbols() -> list[str]:
    pre, _ = s3_list("data/futures/um/monthly/klines/")
    syms = [p.rstrip("/").split("/")[-1] for p in pre]
    return sorted(s for s in syms if s.endswith("USDT"))


def files_for(sym: str) -> list[str]:
    out = []
    for p in (f"data/futures/um/monthly/klines/{sym}/1d/",
              f"data/futures/um/monthly/fundingRate/{sym}/"):
        _, keys = s3_list(p, delimiter=None)
        out += [k[len("data/"):] for k in keys if k.endswith(".zip")]
    return out


def main() -> None:
    syms = um_usdt_symbols()
    print(f"{len(syms)} símbolos USDT-M", flush=True)
    with ThreadPoolExecutor(16) as ex:
        lists = list(ex.map(files_for, syms))
    paths = sorted(p for lst in lists for p in lst)
    (DATA / "um_universe.json").write_text(json.dumps(
        {s: [p for p in lst if "/klines/" in p] for s, lst in zip(syms, lists)}, indent=0))
    print(f"{len(paths)} ficheros", flush=True)
    download(paths, workers=24)


if __name__ == "__main__":
    sys.exit(main())


def download_metrics(symbols: list[str]) -> None:
    """Métricas diarias de futuros (open interest 5 min, ratios long/short)."""
    paths = []
    for s in symbols:
        _, keys = s3_list(f"data/futures/um/daily/metrics/{s}/", delimiter=None)
        paths += [k[len("data/"):] for k in keys if k.endswith(".zip")]
    download(sorted(paths), workers=24)


def download_spot_daily(symbols: list[str]) -> None:
    """Klines spot 1d mensuales (incluidos pares deslistados) para `symbols`."""
    pre, _ = s3_list("data/spot/monthly/klines/")
    spot = {p.rstrip("/").split("/")[-1] for p in pre}
    todo = [s for s in symbols if s in spot]

    def files(sym):
        _, keys = s3_list(f"data/spot/monthly/klines/{sym}/1d/", delimiter=None)
        return [k[len("data/"):] for k in keys if k.endswith(".zip")]

    with ThreadPoolExecutor(16) as ex:
        paths = sorted(p for lst in ex.map(files, todo) for p in lst)
    print(f"{len(todo)} pares con spot, {len(paths)} ficheros", flush=True)
    download(paths, workers=24)


def fill_daily_gaps(market: str = "um", interval: str = "1d") -> int:
    """Descarga ficheros diarios para los días que faltan dentro del rango de cada
    símbolo en los mensuales (p. ej. 2022-02-26/28 y 2022-04-01/02 en perps)."""
    import pandas as pd

    from .data import load_klines
    sub = "futures/um" if market == "um" else "spot"
    base = DATA / sub / "monthly/klines"
    paths = []
    for d in sorted(base.iterdir()):
        if not (d / interval).exists():
            continue
        k = load_klines(market, d.name, interval)
        full = pd.date_range(k.index.min(), k.index.max(), freq="1D", tz="UTC")
        for day in full.difference(k.index):
            ds = day.strftime("%Y-%m-%d")
            paths.append(f"{sub}/daily/klines/{d.name}/{interval}/{d.name}-{interval}-{ds}.zip")
    print(f"{len(paths)} días a rellenar", flush=True)
    download(paths, workers=24)
    return len(paths)
