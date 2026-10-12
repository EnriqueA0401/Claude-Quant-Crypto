"""H009 · G2: reversión del basis spot-perp extremo (largo spot + corto perp), 1h.

Uso: python3 experiments/h009_basis.py
Variantes fijadas en HYPOTHESES.md: p ∈ {0.99, 0.995} × H ∈ {8, 24}.
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
from h001_carry import load  # noqa: E402
from src import metrics  # noqa: E402
from src.carry import run_carry  # noqa: E402
from src.costs import PERP, SPOT  # noqa: E402

TRAIN_END = pd.Timestamp("2023-01-01", tz="UTC")
VARIANTS = [(p, h) for p in (0.99, 0.995) for h in (8, 24)]
WIN = 720


def basis_signal(basis: pd.Series, p: float, hold: int) -> pd.Series:
    """1 = mantener la cobertura. Decisión al close del bar t (usa basis[t] y las WIN
    horas anteriores); con pos[t] = sig[t-1] se ejecuta en el open de t+1."""
    b = basis.to_numpy()
    prev = pd.Series(b)
    pct = prev.rolling(WIN + 1, min_periods=WIN // 2 + 1).apply(
        lambda x: (x[:-1] < x[-1]).mean(), raw=True).to_numpy()
    med = prev.shift(1).rolling(WIN, min_periods=WIN // 2).median().to_numpy()
    sig = np.zeros(len(b))
    held = 0
    for t in range(len(b)):
        if held:
            held += 1
            if b[t] <= med[t] or held > hold:
                held = 0
        elif pct[t] >= p:
            held = 1
        sig[t] = 1.0 if held else 0.0
    return pd.Series(sig, index=basis.index)


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        perp, spot, trad, fund = load(sym)
        m = perp.index < TRAIN_END
        perp, spot, trad = perp[m], spot[m], trad[m]
        fund = fund[fund.index < TRAIN_END]
        from src.data import load_klines
        pc = load_klines("um", sym)["close"].reindex(perp.index)
        sc = load_klines("spot", sym)["close"].reindex(perp.index).ffill()
        basis = (pc / sc - 1).where(trad)
        for p, h in VARIANTS:
            sig = basis_signal(basis.ffill(), p, h)
            out = run_carry(spot, perp, fund, sig, SPOT, PERP, tradable=trad,
                            liq_high=perp["mark_high"])
            entries = int((out["pos"].diff().fillna(0) > 0).sum())
            tr = out[out["pos"] > 0]
            res[f"{sym}|p={p}|H={h}"] = {
                "entries": entries, "ann": float(out["net"].mean() * 24 * 365),
                "net_per_entry": float(out["net"].sum() / max(entries, 1)),
                "basis_per_entry": float(out["basis"].sum() / max(entries, 1)),
                "cost_per_entry": float((out["cost"] + out["rebalance"]).sum() / max(entries, 1)),
                "hours_held": int(len(tr))}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h009_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(5).to_string())


if __name__ == "__main__":
    main()
