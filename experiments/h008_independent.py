"""H008 - reimplementacion independiente (paso 4 del protocolo de revision).

Carry de funding cross-sectional semanal en perps USDT-M, estilo broker:
bucle explicito sobre semanas y posiciones. No reutiliza src/signals.py,
src/backtest.py ni src/carry.py; solo los cargadores de src/data.py.

Uso: python experiments/h008_independent.py
Salida: reports/h008_independent.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_klines, load_funding  # noqa: E402

KL_DIR = ROOT / "data/futures/um/monthly/klines"
OUT = ROOT / "reports/h008_independent.json"
END = pd.Timestamp("2023-01-01", tz="UTC")
TOP_LIQ = 50
N_SIDE = 5
W = 0.1
COST_RATE = 0.0015
MIN_SCORED = 10
DS = [3, 7, 14]
DAY = pd.Timedelta(days=1)


def load_all():
    syms = sorted(p.name for p in KL_DIR.iterdir() if (p / "1d").is_dir())
    opens, highs, closes, qvs, first_bar, fund_events, fund_daily = {}, {}, {}, {}, {}, {}, {}
    for s in syms:
        try:
            df = load_klines("um", s, "1d")
        except FileNotFoundError:
            continue
        if df.empty:
            continue
        opens[s] = df["open"].astype(float)
        highs[s] = df["high"].astype(float)
        closes[s] = df["close"].astype(float)
        qvs[s] = df["quote_volume"].astype(float)
        first_bar[s] = df.index[0]
        try:
            f = load_funding(s)
        except FileNotFoundError:
            continue
        f = f.dropna()
        fund_events[s] = f
        # cada evento en ts se asigna al dia floor(ts - 1ns): el de 00:00 va al dia previo
        day = (f.index - pd.Timedelta(1, "ns")).floor("D")
        fund_daily[s] = f.groupby(day).sum()
    O = pd.DataFrame(opens).sort_index()
    H = pd.DataFrame(highs).reindex(O.index)
    C = pd.DataFrame(closes).reindex(O.index)
    Q = pd.DataFrame(qvs).reindex(O.index)
    F = pd.DataFrame(fund_daily).reindex(O.index).fillna(0.0)
    return syms, O, H, C, Q, first_bar, fund_events, F


def run(D, O, H, C, Q, first_bar, fund_events, F):
    idx = O.index
    qv30 = Q.rolling(30, min_periods=20).sum()
    mondays = [d for d in idx if d.dayofweek == 0 and d < END]
    idxset = set(idx)
    w_prev = {}
    weeks = []
    for i in range(len(mondays) - 1):
        mon, nxt = mondays[i], mondays[i + 1]
        sun = mon - DAY
        if sun not in idxset:
            continue
        # --- universo
        cand = []
        for s in O.columns:
            if np.isnan(O.at[mon, s]):
                continue
            if first_bar[s] > sun - pd.Timedelta(days=90):
                continue
            v = qv30.at[sun, s]
            if np.isnan(v):
                continue
            cand.append((v, s))
        cand.sort(key=lambda x: -x[0])
        univ = [s for _, s in cand[:TOP_LIQ]]
        # --- score: media de funding en [mon-D, mon)
        scores = []
        lo = mon - pd.Timedelta(days=D)
        for s in univ:
            f = fund_events.get(s)
            if f is None:
                continue
            ev = f[(f.index >= lo) & (f.index < mon)]
            if len(ev) == 0:
                continue
            scores.append((float(ev.mean()), s))
        if len(scores) < MIN_SCORED:
            continue
        scores.sort(key=lambda x: x[0])  # empates: orden por nombre via tupla
        longs = [s for _, s in scores[:N_SIDE]]
        shorts = [s for _, s in scores[-N_SIDE:]]
        w_new = {s: W for s in longs}
        w_new.update({s: -W for s in shorts})
        # --- costes
        names = set(w_new) | set(w_prev)
        turnover = sum(abs(w_new.get(s, 0.0) - w_prev.get(s, 0.0)) for s in names)
        cost = turnover * COST_RATE
        w_prev = w_new
        # --- PnL por posicion
        days = idx[(idx >= mon) & (idx < nxt)]
        price_pnl = 0.0
        fund_pnl = 0.0
        for s, w in w_new.items():
            o = O.loc[days, s].dropna()
            if o.empty:
                continue
            p0 = float(o.iloc[0])
            p1 = O.at[nxt, s]
            if np.isnan(p1):
                c = C.loc[days, s].dropna()
                p1 = float(c.iloc[-1])
            r = p1 / p0 - 1.0
            if w < 0:
                hmax = H.loc[days, s].max()
                if not np.isnan(hmax) and hmax >= 2 * p0:
                    r = 1.0
            fsum = float(F.loc[days, s].sum())
            price_pnl += w * r
            fund_pnl += -w * fsum
        net = price_pnl + fund_pnl - cost
        weeks.append({"mon": str(mon.date()), "net": net, "cost": cost,
                      "funding": fund_pnl, "price": price_pnl})
    nets = [w["net"] for w in weeks]
    return {
        "D": D,
        "n_weeks": len(weeks),
        "sum_net": float(np.sum(nets)),
        "mean_net": float(np.mean(nets)) if nets else None,
        "sum_cost": float(sum(w["cost"] for w in weeks)),
        "sum_funding": float(sum(w["funding"] for w in weeks)),
        "sum_price": float(sum(w["price"] for w in weeks)),
        "first3": [(w["mon"], w["net"]) for w in weeks[:3]],
        "weekly": [(w["mon"], w["net"]) for w in weeks],
    }


def main():
    syms, O, H, C, Q, first_bar, fund_events, F = load_all()
    res = {"n_symbols_dirs": len(syms), "n_symbols_loaded": O.shape[1],
           "n_symbols_funding": len(fund_events), "variants": {}}
    for D in DS:
        r = run(D, O, H, C, Q, first_bar, fund_events, F)
        res["variants"][str(D)] = r
        print(D, r["n_weeks"], round(r["sum_net"], 6), round(r["mean_net"], 6),
              round(r["sum_cost"], 6), round(r["sum_funding"], 6), r["first3"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
