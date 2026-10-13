"""H034: corto en el perp tras el anuncio de deslistado spot (Binance, categoría 161).

Uso: python3 experiments/h034_delisting_drift.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from h031_funding_interval import trade  # noqa: E402  (corto: side = −1, liquidación 2×)
import h031_funding_interval as h31  # noqa: E402
from src.external import fetch_binance_announcements  # noqa: E402

h31.COST = 2 * (0.0005 + 0.0015)
TRAIN_END = pd.Timestamp("2024-01-01", tz="UTC")
OOS_END = pd.Timestamp("2025-10-01", tz="UTC")
PAT = re.compile(r"^Binance Will Delist (.+?) on \d{4}-\d{2}-\d{2}")


def parse_tokens(title: str) -> list[str]:
    m = PAT.match(title)
    if not m or any(w in title for w in ("Margin", "Futures", "Pairs")):
        return []
    parts = re.split(r",\s*|\s+and\s+", m.group(1))
    return [p.strip() for p in parts if re.fullmatch(r"[A-Z0-9]+", p.strip())]


def main():
    o, c, h, qv, fd = h5.panel()
    ann = fetch_binance_announcements(161)
    rows = []
    for r in ann.itertuples():
        for tok in parse_tokens(r.title):
            for sym in (f"{tok}USDT", f"1000{tok}USDT"):
                if sym in o.columns:
                    day = r.ts.floor("1D")
                    if day in o.index and not np.isnan(o[sym].get(day, np.nan)):
                        rows.append({"sym": sym, "ts": r.ts, "day": day,
                                     "i": o.index.get_loc(day) + 1})
                    break
    ev = pd.DataFrame(rows)
    ev = ev[ev["day"] < OOS_END - pd.Timedelta("31D")]
    rng = np.random.default_rng(0)
    res = {}
    for n in (7, 30):
        ev[f"net{n}"] = [trade(o, c, h, fd, r.sym, r.i, n, -1.0) for r in ev.itertuples()]
        for name, sel in (("train", ev["day"] < TRAIN_END), ("oos", ev["day"] >= TRAIN_END)):
            part = ev[sel].dropna(subset=[f"net{n}"])
            if len(part) < 3:
                res[f"N={n}|{name}"] = {"events": int(len(part))}
                continue
            alive = o.notna()
            sims = []
            for _ in range(300):
                v = []
                for r in part.itertuples():
                    pool = np.flatnonzero(alive[r.sym].to_numpy())
                    pool = pool[pool < len(o.index) - n - 1]
                    if len(pool):
                        v.append(trade(o, c, h, fd, r.sym, int(rng.choice(pool)), n, -1.0))
                sims.append(np.nanmean(v))
            sims = np.array(sims)
            x = part[f"net{n}"]
            res[f"N={n}|{name}"] = {"events": int(len(x)), "mean_net": float(x.mean()),
                                    "median_net": float(x.median()), "hit": float((x > 0).mean()),
                                    "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))),
                                    "liquidations": int((x <= -1).sum()),
                                    "null_mean": float(sims.mean()),
                                    "p_vs_null": float((sims >= x.mean()).mean())}
    ev.to_csv(ROOT / "reports/h034_events.csv", index=False)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h034.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
