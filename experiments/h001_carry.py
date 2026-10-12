"""H001 · G2: exploración in-sample (train 2020-01 → 2022-12, BTC y ETH).

Uso: python3 experiments/h001_carry.py
6 variantes fijadas antes de ver resultados: theta ∈ {1e-4, 2e-4, 3e-4}, k ∈ {1, 3}.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import metrics  # noqa: E402
from src.carry import carry_signal, run_carry  # noqa: E402
from src.costs import PERP, SPOT  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(theta, k) for theta in (1e-4, 2e-4, 3e-4) for k in (1, 3)]
HPY = 24 * 365


def load(sym):
    perp = load_klines("um", sym)[["open", "high"]]
    spot = load_klines("spot", sym)["open"]
    tradable = spot.reindex(perp.index).notna()
    spot = spot.reindex(perp.index).ffill()
    ok = spot.notna()
    perp["mark_high"] = load_klines("um", sym, kind="markPriceKlines")["high"].reindex(perp.index)
    return perp[ok], spot[ok], tradable[ok], load_funding(sym)


def summarize(out):
    r = out["net"].to_numpy()
    entries = int(((out["pos"].diff().fillna(out["pos"].iloc[0])) > 0).sum())
    lo, hi = metrics.block_bootstrap_mean_ci(r, block=24 * 60, n_boot=2000)
    return {"ann_return": float(r.mean() * HPY), "sharpe_ann": metrics.sharpe_resampled(out["net"]),
            "max_dd": metrics.max_drawdown(r), "entries": entries,
            "time_in_mkt": float(out["pos"].mean()),
            "funding_ann": float(out["funding"].mean() * HPY),
            "basis_ann": float(out["basis"].mean() * HPY),
            "costs_ann": float((out["cost"] + out["rebalance"]).mean() * HPY),
            "liquidations": int(out["liquidated"].sum()),
            "ci95_mean_hourly": [lo, hi]}


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        perp, spot, trad, fund = load(sym)
        m = perp.index < TRAIN_END
        perp, spot, trad = perp[m], spot[m], trad[m]
        fund = fund[fund.index < TRAIN_END]
        for theta, k in VARIANTS:
            sig = carry_signal(fund, perp.index, k, theta)
            out = run_carry(spot, perp, fund, sig, SPOT, PERP, tradable=trad,
                            liq_high=perp["mark_high"])
            res[f"{sym}|theta={theta}|k={k}"] = summarize(out)
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    payload = {"commit": commit, "period": "2020-01-01..2022-12-31", "variants": len(VARIANTS),
               "results": res}
    (ROOT / "reports/h001_g2.json").write_text(json.dumps(payload, indent=1) + "\n")
    df = pd.DataFrame(res).T[["ann_return", "sharpe_ann", "max_dd", "entries", "time_in_mkt",
                              "funding_ann", "basis_ann", "costs_ann", "liquidations"]]
    print(df.astype(float).round(4).to_string())


if __name__ == "__main__":
    main()
