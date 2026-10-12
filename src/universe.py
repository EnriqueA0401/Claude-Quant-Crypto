"""Universo completo de data.binance.vision (incluye pares deslistados) vía listado S3.

Uso: python3 -m src.universe   (lista perps USDT-M y descarga klines 1d + funding)
"""
from __future__ import annotations

import json
import re
import sys
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
        r = s.get(S3, params=params, timeout=60)
        r.raise_for_status()
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
