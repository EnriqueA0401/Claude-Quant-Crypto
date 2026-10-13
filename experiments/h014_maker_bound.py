"""H014 · cota superior: ¿rescata la ejecución maker alguna señal de horizonte corto?

Uso: python3 experiments/h014_maker_bound.py
Supuesto optimista (cota superior): toda orden se llena como maker sin slippage ni
selección adversa. Comisiones Binance VIP0: perp maker 0,02 %; spot maker 0,10 %.
Se recalcula H009 (basis spot-perp 1h, sus 4 variantes) en train con esos costes.
Si la cota superior es negativa, ningún modelo de cola realista puede ser positivo.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
from h001_carry import load  # noqa: E402
from h009_basis import TRAIN_END, VARIANTS, basis_signal  # noqa: E402
from src.carry import run_carry  # noqa: E402
from src.costs import Costs  # noqa: E402
from src.data import load_klines  # noqa: E402

SPOT_MAKER, PERP_MAKER = Costs(0.0010, 0.0), Costs(0.0002, 0.0)


def main():
    res = {}
    for sym in ["BTCUSDT", "ETHUSDT"]:
        perp, spot, trad, fund = load(sym)
        m = perp.index < TRAIN_END
        perp, spot, trad, fund = perp[m], spot[m], trad[m], fund[fund.index < TRAIN_END]
        pc = load_klines("um", sym)["close"].reindex(perp.index)
        sc = load_klines("spot", sym)["close"].reindex(perp.index).ffill()
        basis = (pc / sc - 1).where(trad).ffill()
        for p, h in VARIANTS:
            out = run_carry(spot, perp, fund, basis_signal(basis, p, h), SPOT_MAKER, PERP_MAKER,
                            tradable=trad, liq_high=perp["mark_high"])
            e = int((out["pos"].diff().fillna(0) > 0).sum())
            res[f"{sym}|p={p}|H={h}"] = {
                "entries": e, "ann": float(out["net"].mean() * 24 * 365),
                "basis_per_entry": float(out["basis"].sum() / max(e, 1)),
                "cost_per_entry": float(out["cost"].sum() / max(e, 1)),
                "net_per_entry": float(out["net"].sum() / max(e, 1))}
    (ROOT / "reports/h014_maker_bound.json").write_text(json.dumps(res, indent=1) + "\n")
    print(pd.DataFrame(res).T.round(5).to_string())


if __name__ == "__main__":
    main()
