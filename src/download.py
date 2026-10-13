"""Descarga masiva de ficheros mensuales de data.binance.vision.

Uso: python3 -m src.download  (descarga el conjunto por defecto de H001)
Registra cada sha256 en data_manifest.json y los ficheros inexistentes (404) en
data/missing.json.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import requests

from .data import BASE_URL, DATA, HASH_LEN, manifest_load, manifest_save, sha256

SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"]


def monthly_paths(symbol: str, start: str, end: str) -> list[str]:
    out = []
    for m in pd.period_range(start, end, freq="M"):
        ym = m.strftime("%Y-%m")
        out += [f"spot/monthly/klines/{symbol}/1h/{symbol}-1h-{ym}.zip",
                f"futures/um/monthly/klines/{symbol}/1h/{symbol}-1h-{ym}.zip",
                f"futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{ym}.zip"]
    return out


def _get(rel: str, session: requests.Session) -> tuple[str, str | None]:
    dest = DATA / rel
    if dest.exists():
        blob = dest.read_bytes()
        try:                                   # un corte a mitad de escritura deja un zip roto
            zipfile.ZipFile(io.BytesIO(blob)).testzip()
            return rel, sha256(blob)
        except zipfile.BadZipFile:
            dest.unlink()
    for attempt in range(4):
        try:
            r = session.get(f"{BASE_URL}/{rel}", timeout=60)
            if r.status_code == 404:
                return rel, None
            r.raise_for_status()
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            tmp.write_bytes(r.content)
            tmp.replace(dest)                  # escritura atómica
            return rel, sha256(r.content)
        except requests.RequestException:
            if attempt == 3:
                raise
    raise RuntimeError("inalcanzable")


def download(paths: list[str], workers: int = 16) -> None:
    man = manifest_load()
    missing = []
    s = requests.Session()
    ad = requests.adapters.HTTPAdapter(pool_connections=workers, pool_maxsize=workers)
    s.mount("https://", ad)
    done = 0
    with ThreadPoolExecutor(workers) as ex:
        for fut in as_completed([ex.submit(_get, p, s) for p in paths]):
            rel, digest = fut.result()
            done += 1
            if digest is None:
                missing.append(rel)
            else:
                digest = digest[:HASH_LEN]
                if man.get(rel) not in (None, digest):
                    raise RuntimeError(f"hash distinto para {rel}")
                man[rel] = digest
            if done % 100 == 0 or done == len(paths):
                print(f"{done}/{len(paths)} ({len(missing)} inexistentes)", flush=True)
    manifest_save(man)
    mpath = DATA / "missing.json"
    prev = set(json.loads(mpath.read_text())) if mpath.exists() else set()
    prev -= set(man)  # ficheros que ahora sí existen
    mpath.write_text(json.dumps(sorted(prev | set(missing)), indent=1) + "\n")


if __name__ == "__main__":
    end = sys.argv[1] if len(sys.argv) > 1 else "2026-09"
    paths = [p for sym in SYMBOLS for p in monthly_paths(sym, "2020-01", end)]
    download(paths)
