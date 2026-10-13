"""H042 (contraste, no operable): carry siempre cubierto con trimestrales de Deribit, 2018–2026.

Uso: python3 experiments/h042_deribit_carry.py
Regla de H033 sin cambios, en barras diarias. Spot de referencia: Binance diario.
Tipos de caja: medias anuales APROXIMADAS de letras del Tesoro de EE. UU. a 3 meses.
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
from src.data import load_klines  # noqa: E402
from src.external import deribit_quarterly_names, fetch_deribit_future_daily  # noqa: E402

h12.W, h12.MMR, h12.CS, h12.CF = 1.0, -1e9, 0.0, 0.0010
CASH_APPROX = {2018: 0.019, 2019: 0.021, 2020: 0.004, 2021: 0.0005, 2022: 0.020,
               2023: 0.050, 2024: 0.050, 2025: 0.042, 2026: 0.038}
END = pd.Timestamp("2026-10-01", tz="UTC")


def main():
    nets = {}
    for cur, spot_sym in (("BTC", "BTCUSDT"), ("ETH", "ETHUSDT")):
        futs = {}
        for n in deribit_quarterly_names(cur):
            df = fetch_deribit_future_daily(n)
            if df is not None and len(df) > 20:
                futs[f"{cur}_{df.index[-1].strftime('%y%m%d')}"] = df[["open", "high", "close"]]
        spot = load_klines("spot", spot_sym, "1d")[["open", "close"]]
        o = h12.run(spot, futs, -1.0, "expiry", end=END)
        first = min(f.index[0] for f in futs.values())
        nets[cur] = o["net"][o.index >= first]
    res = {}
    for cur, r in nets.items():
        yearly = r.groupby(r.index.year).sum()
        days = r.groupby(r.index.year).size()
        res[cur] = {"period": f"{r.index[0].date()}..{r.index[-1].date()}",
                    "ann": float(r.mean() * 365), "sharpe_m": metrics.sharpe_resampled(r),
                    "max_dd": metrics.max_drawdown(r.to_numpy()),
                    "yearly": {int(y): {"ret": float(v), "days": int(days[y]),
                                        "cash_approx": CASH_APPROX.get(int(y)),
                                        "beats_cash": bool(v / days[y] * 365 > CASH_APPROX.get(int(y), 0))}
                               for y, v in yearly.items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h042.json").write_text(json.dumps({"commit": commit, "results": res},
                                                       indent=1) + "\n")
    for cur, v in res.items():
        print(cur, v["period"], "anual", round(v["ann"], 4), "Sharpe", round(v["sharpe_m"], 2),
              "MDD", round(v["max_dd"], 3))
        for y, yv in v["yearly"].items():
            ann = yv["ret"] / yv["days"] * 365
            print("  ", y, "carry anualizado", round(ann, 4), "| caja ≈", yv["cash_approx"],
                  "| supera:", yv["beats_cash"])


if __name__ == "__main__":
    main()
