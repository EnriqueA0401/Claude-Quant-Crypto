"""H018 · G2/G3: largo tras purga de apalancamiento diaria (OI cae ≥ θ y el día es rojo).

Uso: python3 experiments/h018_oi_flush.py   (requiere experiments/h018_universe.py)
Variantes fijadas en HYPOTHESES.md: θ ∈ {0.10, 0.15} × N ∈ {7, 28} días.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from src.data import load_oi_hourly  # noqa: E402

COST = 2 * 0.0015
TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")
VARIANTS = [(th, n) for th in (0.10, 0.15) for n in (7, 28)]


def trade(o, c, fd, s, i, n):
    """Largo desde open[i] durante n días; salida en open[i+n] o último close."""
    idx = o.index
    p0 = o[s].iloc[i]
    if np.isnan(p0):
        return np.nan
    j = i + n
    p1 = o[s].iloc[j] if j < len(idx) else np.nan
    if np.isnan(p1):
        seg = c[s].iloc[i:j].dropna()
        if not len(seg):
            return np.nan
        p1 = seg.iloc[-1]
    fsum = fd[s].iloc[i:min(j, len(idx))].sum() if s in fd else 0.0
    return p1 / p0 - 1 - fsum - COST


def events(o, c, qv, oi, th, n, end):
    vol30 = qv.rolling(30, min_periods=20).sum()
    rank = vol30.rank(axis=1, ascending=False)
    r = c.pct_change(fill_method=None)
    out = []
    for s, x in oi.items():
        chg = x / x.shift(1) - 1
        busy = -1
        cond = (chg <= -th) & (r[s].reindex(chg.index) < 0) & (rank[s].reindex(chg.index) <= 30)
        for d in chg.index[cond.fillna(False).to_numpy()]:
            if d >= end:
                break
            i = o.index.get_loc(d) + 1                  # entrada en el open del día siguiente
            if i <= busy or i >= len(o.index):
                continue
            out.append({"sym": s, "day": d, "i": i})
            busy = i + n - 1
    return pd.DataFrame(out)


def main():
    o, c, h, qv, fd = h5.panel()
    syms = json.loads((ROOT / "reports/h018_universe.json").read_text())
    oi = {}
    for s in syms:
        try:
            oi[s] = load_oi_hourly(s).resample("1D").last().reindex(o.index)
        except FileNotFoundError:
            pass
    rng = np.random.default_rng(0)
    vol30 = qv.rolling(30, min_periods=20).sum()
    inuni = (vol30.rank(axis=1, ascending=False) <= 30)
    res = {}
    for th, n in VARIANTS:
        ev = events(o, c, qv, oi, th, n, HOLDOUT - pd.Timedelta(days=n + 1))
        ev["net"] = [trade(o, c, fd, s, i, n) for s, i in zip(ev["sym"], ev["i"])]
        ev = ev.dropna(subset=["net"])
        for name, part in (("train", ev[ev["day"] < TRAIN_END]), ("oos", ev[ev["day"] >= TRAIN_END])):
            if len(part) < 2:
                res[f"theta={th}|N={n}|{name}"] = {"events": int(len(part))}
                continue
            # nulo: mismo símbolo, día aleatorio en el que estaba en el universo y en el periodo
            lo_d, hi_d = (o.index[0], TRAIN_END) if name == "train" else (TRAIN_END, HOLDOUT - pd.Timedelta(days=n + 1))
            pool = {s: np.flatnonzero(inuni[s].to_numpy() & (o.index >= lo_d) & (o.index < hi_d))
                    for s in part["sym"].unique()}
            sims = []
            for _ in range(300):
                v = [trade(o, c, fd, s, int(rng.choice(pool[s])) + 1, n)
                     for s in part["sym"] if len(pool[s])]
                sims.append(np.nanmean(v))
            sims = np.array(sims)
            m = part["net"].mean()
            res[f"theta={th}|N={n}|{name}"] = {
                "events": int(len(part)), "symbols": int(part["sym"].nunique()),
                "mean_net": float(m), "median_net": float(part["net"].median()),
                "hit": float((part["net"] > 0).mean()),
                "t": float(m / (part["net"].std(ddof=1) / np.sqrt(len(part)))),
                "null_mean": float(sims.mean()), "p_vs_null": float((sims >= m).mean())}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h018.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
