"""H025: largo BTC/ETH (perp) solo si la prima de varianza supera su mediana de 52 semanas.

Uso: python3 experiments/h025_vrp.py
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
from h024_vol_managed import COST, HOLDOUT, TRAIN, stats  # noqa: E402
from src.data import load_funding, load_klines  # noqa: E402
from src.external import fetch_dvol  # noqa: E402


def vrp_signal(close: pd.Series, dvol: pd.Series, rvwin: int) -> pd.Series:
    """Señal diaria (1 = largo) decidida al close de cada domingo y mantenida la semana.

    close: closes diarios (índice = open time del día, UTC). dvol: DVOL diario de Deribit
    (close del día, mismo índice). VRP = (DVOL/100)² − varianza realizada anualizada de
    `rvwin` días; largo si VRP del domingo > mediana de los 52 domingos anteriores
    (mín. 26; sin historia → largo). La posición del día t es signal[t−1]."""
    lr = np.log(close).diff()
    rv2 = lr.rolling(rvwin, min_periods=rvwin - 1).var() * 365
    iv2 = (dvol.reindex(close.index).ffill() / 100) ** 2
    vrp = iv2 - rv2
    wk = vrp[pd.Series(close.index.dayofweek == 6, index=close.index)]
    med = wk.shift(1).rolling(52, min_periods=26).median()
    sig_w = (wk > med).astype(float).where(med.notna(), 1.0)
    return sig_w.reindex(close.index).ffill().fillna(1.0)


def asset(sym, cur, rvwin):
    k = load_klines("um", sym, "1d")
    k = k[(k.index >= pd.Timestamp("2021-03-24", tz="UTC")) & (k.index < HOLDOUT)]
    sig = vrp_signal(k["close"], fetch_dvol(cur), rvwin)
    pos = sig.shift(1).fillna(0.0)
    ret = k["open"].shift(-1) / k["open"] - 1
    f = load_funding(sym)
    fday = f.groupby((f.index - pd.Timedelta("1ns")).floor("1D")).sum().reindex(k.index).fillna(0.0)
    net = pos * ret - pos * fday - pos.diff().abs().fillna(0.0) * COST
    bh = ret - fday
    keep = k.index >= TRAIN[0]
    return net[keep].iloc[:-1], bh[keep].iloc[:-1], pos[keep].iloc[:-1]


def main():
    res = {}
    for w in (7, 30):
        parts = [asset("BTCUSDT", "BTC", w), asset("ETHUSDT", "ETH", w)]
        net = pd.concat([p[0] for p in parts], axis=1).mean(axis=1)
        bh = pd.concat([p[1] for p in parts], axis=1).mean(axis=1)
        pos = pd.concat([p[2] for p in parts], axis=1).mean(axis=1)
        tr, te = net.index < TRAIN[1], net.index >= TRAIN[1]
        res[f"rv{w}"] = {"train": stats(net[tr], bh[tr]), "oos": stats(net[te], bh[te]),
                         "exposure_oos": float(pos[te].mean())}
    res["chosen_on_train"] = max(("rv7", "rv30"), key=lambda k: res[k]["train"]["sharpe_m"])
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h025.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for k in ("rv7", "rv30"):
        for p in ("train", "oos"):
            v = res[k][p]
            print(k, p, "ann", round(v["ann"], 3), "SR", round(v["sharpe_m"], 2), "MDD",
                  round(v["max_dd"], 2), "| B&H", round(v["bh_ann"], 3), round(v["bh_sharpe_m"], 2),
                  "| alfa", round(v["alpha_ann"], 3), "beta", round(v["beta"], 2),
                  [round(x, 5) for x in v["alpha_ci95_daily"]])
    print("elegida:", res["chosen_on_train"])


if __name__ == "__main__":
    main()
