"""H006 · G2: corto en perps USDT-M recién listados (listados 2020-01 → 2022-12).

Uso: python3 experiments/h006_listing.py   (requiere python3 -m src.universe)
Variantes fijadas en HYPOTHESES.md antes de ver resultados: E ∈ {1, 2} × N ∈ {7, 14, 30}.
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import DATA, load_funding, load_klines  # noqa: E402

FEE, SLIP = 0.0005, 0.0015
TRAIN = (pd.Timestamp("2020-01-02", tz="UTC"), pd.Timestamp("2023-01-01", tz="UTC"))
VARIANTS = [(e, n, None) for e in (1, 2) for n in (7, 14, 30)] + \
    [(2, n, x) for n in (7, 14, 30) for x in (0.3, 0.6)]


def symbols():
    d = DATA / "futures/um/monthly/klines"
    return sorted(p.name for p in d.iterdir() if (p / "1d").exists())


def event_return(k, f, start, n, stop=None):
    """Corto 1x desde open[start] durante n días (o hasta el último dato).

    stop: si el high diario alcanza p0·(1+stop) se cierra en max(nivel, open del día)
    más slippage; se comprueba antes que la liquidación (el stop está por debajo).
    """
    seg = k.iloc[start:start + n]
    if len(seg) == 0:
        return None
    p0 = seg["open"].iloc[0]
    if stop is not None:
        hit = np.flatnonzero(seg["high"].to_numpy() >= p0 * (1 + stop))
        if len(hit):
            j = hit[0]
            fill = max(p0 * (1 + stop), seg["open"].iloc[j]) * (1 + SLIP)
            t0, t1 = seg.index[0], seg.index[j] + pd.Timedelta("12h")
            fund = f[(f.index > t0) & (f.index <= t1)].sum() if f is not None else 0.0
            gross = -(fill / p0 - 1)
            return {"net": gross + fund - 2 * FEE - SLIP, "gross": gross,
                    "funding": float(fund), "liquidated": False, "stopped": True,
                    "days": j + 1, "t0": t0, "t1": t1}
    if (seg["high"] >= 2 * p0).any():
        return {"net": -1.0, "liquidated": True, "days": len(seg)}
    end = start + n
    p1 = k["open"].iloc[end] if end < len(k) else seg["close"].iloc[-1]
    t0 = seg.index[0]
    t1 = k.index[end] if end < len(k) else seg.index[-1] + pd.Timedelta("1D")
    fund = f[(f.index > t0) & (f.index <= t1)].sum() if f is not None else 0.0
    gross = -(p1 / p0 - 1)
    return {"net": gross + fund - 2 * (FEE + SLIP), "gross": gross, "funding": float(fund),
            "liquidated": False, "days": len(seg), "t0": t0, "t1": t1}


def collect_events(start, end, data_end=None):
    """Eventos de listados en [start, end). data_end: se descartan los eventos cuya
    ventana llegue a data_end (purga frente al holdout)."""
    btc = load_klines("um", "BTCUSDT", "1d")
    events = []
    for sym in symbols():
        if sym == "BTCUSDT":
            continue
        k = load_klines("um", sym, "1d")
        first = k.index[0]
        if not (start <= first < end):
            continue      # 2020-01-01 = inicio de los datos, no un listado
        try:
            f = load_funding(sym)
        except FileNotFoundError:
            f = None
        for e, n, x in VARIANTS:
            kk = k if data_end is None else k[k.index < data_end]
            r = event_return(kk, f, e, n, x)
            if r is None:
                continue
            if data_end is not None and r.get("t1", first) >= data_end - pd.Timedelta("1D"):
                continue
            bt = None
            if not r["liquidated"]:
                b0 = btc["open"].asof(r["t0"])
                b1 = btc["open"].asof(r["t1"])
                bt = -(b1 / b0 - 1)
            events.append({"sym": sym, "listed": str(first.date()), "E": e, "N": n,
                           "stop": x if x is not None else 0.0,
                           "net": r["net"], "liquidated": r["liquidated"],
                           "btc_short": bt, "days": r["days"]})
    return pd.DataFrame(events)


def main():
    df = collect_events(*TRAIN)
    df.to_csv(ROOT / "reports/h006_events.csv", index=False)
    rng = np.random.default_rng(0)
    res = {}
    for (e, n, x), g in df.groupby(["E", "N", "stop"]):
        month = pd.to_datetime(g["listed"]).dt.to_period("M")
        by_m = g.groupby(month)["net"].apply(list)
        boots = []
        for _ in range(5000):
            pick = rng.integers(0, len(by_m), len(by_m))
            boots.append(np.mean(np.concatenate([by_m.iloc[i] for i in pick])))
        excess = (g["net"] - g["btc_short"]).dropna()
        res[f"E={e}|N={n}|stop={x}"] = {
            "events": int(len(g)), "mean_net": float(g["net"].mean()),
            "median_net": float(g["net"].median()), "hit": float((g["net"] > 0).mean()),
            "liquidations": int(g["liquidated"].sum()),
            "ci95_cluster_month": [float(np.quantile(boots, 0.025)),
                                   float(np.quantile(boots, 0.975))],
            "mean_minus_btc_short": float(excess.mean()), "months": int(len(by_m))}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h006_g2.json").write_text(json.dumps(
        {"commit": commit, "variants": len(VARIANTS), "results": res}, indent=1) + "\n")
    print(pd.DataFrame(res).T.to_string())


if __name__ == "__main__":
    main()
