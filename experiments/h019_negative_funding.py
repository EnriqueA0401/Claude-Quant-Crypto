"""H019: largo tras inicio de un episodio de funding negativo sostenido (3 días).

Uso: python3 experiments/h019_negative_funding.py
Variantes fijadas en HYPOTHESES.md: u ∈ {0, −1e-4} × N ∈ {7, 14}.
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
from h018_oi_flush import trade  # noqa: E402
from src.data import load_funding  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")
VARIANTS = [(u, n) for u in (0.0, -1e-4) for n in (7, 14)]


def funding_3d(f: pd.Series, days: pd.DatetimeIndex) -> pd.Series:
    """Media equivalente 8 h de los eventos con ts en (d−3 días, d+1 00:00] para cada d."""
    daily = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(days).fillna(0.0)
    return daily.rolling(3, min_periods=3).sum() / 9


def events(o, qv, fund, u, n, end):
    vol30 = qv.rolling(30, min_periods=20).sum()
    rank = vol30.rank(axis=1, ascending=False)
    out = []
    for s, f in fund.items():
        m = funding_3d(f, o.index)
        cond = (m < u) & (m.shift(3) >= u) & (rank[s] <= 30)
        busy = -1
        for d in o.index[cond.fillna(False).to_numpy()]:
            if d >= end:
                break
            i = o.index.get_loc(d) + 1
            if i <= busy or i >= len(o.index):
                continue
            out.append({"sym": s, "day": d, "i": i})
            busy = i + n - 1
    return pd.DataFrame(out)


def main():
    o, c, h, qv, fd = h5.panel()
    syms = json.loads((ROOT / "reports/h018_universe.json").read_text())
    fund = {}
    for s in syms:
        try:
            fund[s] = load_funding(s)
        except FileNotFoundError:
            pass
    rng = np.random.default_rng(0)
    inuni = qv.rolling(30, min_periods=20).sum().rank(axis=1, ascending=False) <= 30
    res = {}
    for u, n in VARIANTS:
        ev = events(o, qv, fund, u, n, HOLDOUT - pd.Timedelta(days=n + 1))
        ev["net"] = [trade(o, c, fd, s, i, n) for s, i in zip(ev["sym"], ev["i"])]
        ev = ev.dropna(subset=["net"])
        for name, part in (("train", ev[ev["day"] < TRAIN_END]), ("oos", ev[ev["day"] >= TRAIN_END])):
            if len(part) < 2:
                res[f"u={u}|N={n}|{name}"] = {"events": int(len(part))}
                continue
            lo_d, hi_d = (o.index[0], TRAIN_END) if name == "train" else (TRAIN_END, HOLDOUT - pd.Timedelta(days=n + 1))
            pool = {s: np.flatnonzero(inuni[s].to_numpy() & (o.index >= lo_d) & (o.index < hi_d))
                    for s in part["sym"].unique()}
            sims = np.array([np.nanmean([trade(o, c, fd, s, int(rng.choice(pool[s])) + 1, n)
                                         for s in part["sym"] if len(pool[s])]) for _ in range(300)])
            m = part["net"].mean()
            res[f"u={u}|N={n}|{name}"] = {
                "events": int(len(part)), "symbols": int(part["sym"].nunique()),
                "mean_net": float(m), "median_net": float(part["net"].median()),
                "hit": float((part["net"] > 0).mean()),
                "t": float(m / (part["net"].std(ddof=1) / np.sqrt(len(part)))),
                "null_mean": float(sims.mean()), "p_vs_null": float((sims >= m).mean())}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h019.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(4).to_string())


if __name__ == "__main__":
    main()
