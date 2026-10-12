"""H008 · G2: carry cross-sectional de funding en perps USDT-M (train 2020–2022).

Uso: python3 experiments/h008_funding_xs.py
Reutiliza el motor de H005 (experiments/h005_xs_momentum.run) con otra puntuación.
"""
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h005_xs_momentum import panel, run  # noqa: E402
from src import metrics  # noqa: E402
from src.data import load_funding  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
DAYS = (3, 7, 14)


def funding_events(names):
    ev = {}
    for s in names:
        try:
            ev[s] = load_funding(s)
        except FileNotFoundError:
            pass
    return ev


def make_score(ev, d):
    def score(sun, mon, names):
        out = {}
        for s in names:
            f = ev.get(s)
            if f is None:
                continue
            w = f[(f.index >= mon - pd.Timedelta(days=d)) & (f.index < mon)]
            if len(w):
                # equivalente a 8 h: suma de la ventana / nº de periodos de 8 h. Así un
                # par con funding cada 4 h o 1 h no queda infravalorado (revisión paso 5)
                out[s] = -w.sum() / (d * 3)   # funding bajo → largo
        return pd.Series(out, dtype=float)
    return score


def main():
    o, c, h, qv, fd = panel()
    ev = funding_events(o.columns)
    res, series = {}, {}
    for d in DAYS:
        df = run(o, c, h, qv, fd, 1, "mom", end=TRAIN_END, score_fn=make_score(ev, d))
        r = df["net"]
        series[f"D={d}"] = r
        lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=8, n_boot=5000)
        res[f"D={d}"] = {"weeks": int(len(r)), "ann": float(r.mean() * 52),
                         "sharpe_m": metrics.sharpe_resampled(r),
                         "max_dd": metrics.max_drawdown(r.to_numpy()),
                         "cost_ann": float(df["cost"].mean() * 52), "ci95_weekly": [lo, hi]}
    pd.DataFrame(series).to_csv(ROOT / "reports/h008_g2_weekly.csv")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h008_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(DAYS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
