"""H012 · G3: walk-forward (selección por Sharpe mensual en train, folds de 6 meses).

Uso: python3 experiments/h012_g3_walkforward.py
Cartera: media de BTC y ETH con la misma variante. Holdout desde 2025-10-01 intacto
(solo contratos que vencen antes).
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h012_quarterly_basis as h12  # noqa: E402
from src import metrics  # noqa: E402


def main():
    runs = {}
    for base in ("BTCUSDT", "ETHUSDT"):
        spot, futs = h12.load(base)
        futs = {c: f for c, f in futs.items() if f.index[-1] < h12.HOLDOUT}
        for th, ex in h12.VARIANTS:
            runs[(base, th, ex)] = h12.run(spot, futs, th, ex, end=h12.HOLDOUT)
    port = {v: pd.concat([runs[(b,) + v] for b in ("BTCUSDT", "ETHUSDT")], axis=1,
                         keys=["B", "E"]) for v in h12.VARIANTS}
    net = {v: (p.xs("net", axis=1, level=1).mean(axis=1)) for v, p in port.items()}
    entries = {v: p.xs("entry", axis=1, level=1).sum(axis=1) for v, p in port.items()}
    edges = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), h12.HOLDOUT,
                                          freq="6MS")) + [h12.HOLDOUT]))
    oos, ent, folds = [], 0, []
    for a, b in zip(edges[:-1], edges[1:]):
        sc = {v: metrics.sharpe_resampled(r[r.index < a - pd.Timedelta("7D")]) for v, r in net.items()}
        best = max(sc, key=sc.get)
        seg = net[best][(net[best].index >= a) & (net[best].index < b)]
        e = int(entries[best][(entries[best].index >= a) & (entries[best].index < b)].sum())
        oos.append(seg)
        ent += e
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": f"theta={best[0]},{best[1]}",
                      "ann": float(seg.mean() * h12.HPY), "entries": e})
    R = pd.concat(oos)
    lo, hi = metrics.block_bootstrap_mean_ci(R.to_numpy(), block=24 * 60, n_boot=2000)
    summ = {"oos_ann": float(R.mean() * h12.HPY), "oos_sharpe_m": metrics.sharpe_resampled(R),
            "oos_mdd": metrics.max_drawdown(R.to_numpy()), "oos_entries": ent,
            "ci95_hourly": [lo, hi],
            "yearly": {int(y): float(v) for y, v in R.groupby(R.index.year).sum().items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h012_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(json.dumps({"folds": folds, "summary": summ}, indent=1))


if __name__ == "__main__":
    main()
