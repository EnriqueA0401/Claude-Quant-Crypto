"""H028: convergencia entre trimestrales COIN-M y USDT-M del mismo vencimiento.

Uso: python3 experiments/h028_cm_um_spread.py
Reutiliza el motor de H012: la pata "spot" es el contrato barato y el "futuro" el caro.
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
from src.data import DATA, load_klines  # noqa: E402

h12.CS = h12.CF = 0.0010          # ambas patas son futuros: 0,05 % + 0,05 % por lado
START = pd.Timestamp("2023-01-01", tz="UTC")


def pairs(base):
    out = []
    for d in sorted((DATA / "futures/um/monthly/klines").glob(f"{base}USDT_*")):
        exp = d.name.split("_")[1]
        cm = DATA / f"futures/cm/monthly/klines/{base}USD_{exp}"
        if (cm / "1h").exists() and (d / "1h").exists():
            um_k = h12.clean_contract(load_klines("um", d.name), d.name)
            cm_k = h12.clean_contract(load_klines("cm", cm.name), cm.name)
            if len(um_k) and len(cm_k) and um_k.index[-1] < h12.HOLDOUT:
                out.append((exp, um_k, cm_k))
    return out


def run_pair(cheap, rich, name, s):
    """Largo `cheap` (como pata spot) y corto `rich` (como futuro)."""
    idx = cheap.index.intersection(rich.index)
    sp = cheap.loc[idx, ["open", "close"]].ffill()
    return h12.run(sp, {name: rich.loc[idx]}, s, "early")


def main():
    res, series = {}, {}
    for s in (0.05, 0.10):
        nets, ent = [], 0
        for base in ("BTC", "ETH"):
            for exp, um, cm in pairs(base):
                a = run_pair(um, cm, f"X_{exp}", s)     # CM caro: corto CM, largo UM
                b = run_pair(cm, um, f"X_{exp}", s)     # UM caro: corto UM, largo CM
                nets += [a["net"], b["net"]]
                ent += int(a["entry"].sum() + b["entry"].sum())
        R = pd.concat(nets, axis=1).fillna(0.0).sum(axis=1) / 4   # capital repartido
        series[s] = R
        for part, sel in (("train", R.index < START), ("oos", R.index >= START)):
            r = R[sel]
            lo, hi = metrics.block_bootstrap_mean_ci(r.to_numpy(), block=24 * 30, n_boot=2000)
            res[f"s={s}|{part}"] = {"ann": float(r.mean() * 8760), "sharpe_m": metrics.sharpe_resampled(r),
                                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                                    "ci95_hourly": [lo, hi], "entries_total": ent}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h028.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k, v in res.items():
        print(k, round(v["ann"], 4), round(v["sharpe_m"], 2), round(v["max_dd"], 3),
              v["entries_total"], [f"{x:.2e}" for x in v["ci95_hourly"]])


if __name__ == "__main__":
    main()
