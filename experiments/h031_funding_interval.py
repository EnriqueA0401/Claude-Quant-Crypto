"""H031: operar contra el lado apalancado tras el acortamiento del intervalo de funding.

Uso: python3 experiments/h031_funding_interval.py
"""
import io
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from src.data import DATA  # noqa: E402

COST = 2 * 0.0015
TRAIN = (pd.Timestamp("2023-01-01", tz="UTC"), pd.Timestamp("2024-07-01", tz="UTC"))
OOS_END = pd.Timestamp("2025-10-01", tz="UTC")


def funding_raw(sym):
    files = sorted((DATA / "futures/um/monthly/fundingRate" / sym).glob("*.zip"))
    if not files:
        return None
    dfs = []
    for f in files:
        with zipfile.ZipFile(f) as z:
            dfs.append(pd.read_csv(io.BytesIO(z.read(z.namelist()[0]))))
    df = pd.concat(dfs)
    df.index = pd.to_datetime(df["calc_time"].astype("int64"), unit="ms", utc=True).round("1min")
    df = df[~df.index.duplicated()].sort_index()
    return df[["funding_interval_hours", "last_funding_rate"]].astype(float)


def find_events(df):
    """Primer acortamiento del intervalo; signo = media de los 3 últimos eventos."""
    iv = df["funding_interval_hours"]
    sw = np.flatnonzero((iv < iv.shift(1)).to_numpy())
    if not len(sw):
        return []
    i = sw[0]
    m = df["last_funding_rate"].iloc[max(0, i - 2):i + 1].mean()
    return [(df.index[i], -np.sign(m))] if m != 0 else []


def trade(o, c, h, fd, s, i, n, side):
    idx = o.index
    if i >= len(idx) or np.isnan(o[s].iloc[i]):
        return np.nan
    p0 = o[s].iloc[i]
    j = i + n
    seg_h = h[s].iloc[i:j]
    if side < 0 and (seg_h >= 2 * p0).any():
        return -1.0
    p1 = o[s].iloc[j] if j < len(idx) else np.nan
    if np.isnan(p1):
        seg = c[s].iloc[i:j].dropna()
        if not len(seg):
            return np.nan
        p1 = seg.iloc[-1]
    fsum = fd[s].iloc[i:min(j, len(idx))].sum() if s in fd else 0.0
    return side * (p1 / p0 - 1) - side * fsum - COST


def main():
    o, c, h, qv, fd = h5.panel()
    events = []
    for s in o.columns:
        df = funding_raw(s)
        if df is None:
            continue
        for ts, side in find_events(df):
            day = ts.floor("1D")
            if TRAIN[0] <= day < OOS_END - pd.Timedelta("8D") and day in o.index:
                events.append({"sym": s, "day": day, "i": o.index.get_loc(day) + 1, "side": side})
    ev = pd.DataFrame(events)
    rng = np.random.default_rng(0)
    res = {}
    for n in (3, 7):
        ev[f"net{n}"] = [trade(o, c, h, fd, r.sym, r.i, n, r.side) for r in ev.itertuples()]
        for name, sel in (("train", ev["day"] < TRAIN[1]), ("oos", ev["day"] >= TRAIN[1])):
            part = ev[sel].dropna(subset=[f"net{n}"])
            if len(part) < 3:
                res[f"N={n}|{name}"] = {"events": int(len(part))}
                continue
            lo, hi = (TRAIN[0], TRAIN[1]) if name == "train" else (TRAIN[1], OOS_END - pd.Timedelta("8D"))
            alive = o.notna()
            sims = []
            for _ in range(300):
                v = []
                for r in part.itertuples():
                    pool = np.flatnonzero(alive[r.sym].to_numpy() & (o.index >= lo) & (o.index < hi))
                    if len(pool):
                        v.append(trade(o, c, h, fd, r.sym, int(rng.choice(pool)), n, r.side))
                sims.append(np.nanmean(v))
            sims = np.array(sims)
            x = part[f"net{n}"]
            res[f"N={n}|{name}"] = {"events": int(len(x)), "mean_net": float(x.mean()),
                                    "median_net": float(x.median()), "hit": float((x > 0).mean()),
                                    "t": float(x.mean() / (x.std(ddof=1) / np.sqrt(len(x)))),
                                    "share_short": float((part["side"] < 0).mean()),
                                    "null_mean": float(sims.mean()),
                                    "p_vs_null": float((sims >= x.mean()).mean())}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h031.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
