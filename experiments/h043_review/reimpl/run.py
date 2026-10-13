"""Event-driven reimplementation: weekly taker-buy-ratio cross-sectional L/S on USDT-M perps."""
import pickle, json, sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
bars, fund = pickle.load(open(HERE / "panel.pkl", "rb"))
QV_ZERO_AS_NAN = "--qvnan" in sys.argv  # sensitivity: count qv<=0 days as non-observations
FUND_STOP_ON_LIQ = "--fundstop" in sys.argv
DRIFT = "--drift" in sys.argv  # funding on drifted notional (daily mid price proxy)  # sensitivity: no funding after liquidation day

# ---------- panels (signal side) ----------
O = pd.DataFrame({s: d["open"] for s, d in bars.items()}).sort_index()
H = pd.DataFrame({s: d["high"] for s, d in bars.items()}).reindex(O.index)
C = pd.DataFrame({s: d["close"] for s, d in bars.items()}).reindex(O.index)
QV = pd.DataFrame({s: d["quote_volume"] for s, d in bars.items()}).reindex(O.index)
TB = pd.DataFrame({s: d["taker_buy_quote"] for s, d in bars.items()}).reindex(O.index)
full = pd.date_range(O.index.min(), O.index.max(), freq="D")
assert O.index.equals(full), "daily index has gaps"
dead = ~(QV > 0)  # qv<=0 or missing
O, H, C, TB = O.mask(dead), H.mask(dead), C.mask(dead), TB.mask(dead)
if QV_ZERO_AS_NAN:
    QV = QV.mask(dead)
first_valid = O.apply(lambda s: s.first_valid_index())
dates = set(O.index)
qv30 = QV.rolling(30, min_periods=20).sum()

# funding: dict sym -> Series (ts naive UTC)
FUND = {s: f.sort_index() for s, f in fund.items() if len(f)}

FEE = 0.0015
DAY = pd.Timedelta(days=1)


def select(mon):
    sun = mon - DAY
    if sun not in dates or (sun - 7 * DAY) not in dates or mon not in dates:
        return None
    o = O.loc[mon]
    elig = [s for s in O.columns if pd.notna(o[s]) and pd.notna(first_valid[s])
            and first_valid[s] <= sun - 90 * DAY]
    liq = qv30.loc[sun, elig].dropna().sort_values(ascending=False, kind="mergesort")
    # deterministic tiebreak by name for equal volumes
    liq = liq.reset_index().sort_values([sun, "index"], ascending=[False, True]).set_index("index")[sun]
    uni = list(liq.index[:50])
    win = slice(sun - 6 * DAY, sun)
    tb, qv = TB.loc[win, uni], QV.loc[win, uni]
    tbs = tb.sum(min_count=5).where(tb.notna().sum() >= 5)
    qvs = qv.sum(min_count=5).where(qv.notna().sum() >= 5)
    sc = (tbs / qvs).replace([np.inf, -np.inf], np.nan).dropna()
    if len(sc) < 10:
        return None
    df = pd.DataFrame({"sc": sc.round(10).values, "sym": sc.index}).sort_values(["sc", "sym"])
    shorts = list(df["sym"].iloc[:5]); longs = list(df["sym"].iloc[-5:])
    w = {s: 0.1 for s in longs}
    w.update({s: -0.1 for s in shorts})
    return w, {s: float(sc[s]) for s in w}


def hold_week(mon, w):
    """Event-driven holding: day loop, portfolio dict, funding per event, daily liquidation check."""
    nxt = mon + 7 * DAY
    port = {s: {"w": wt, "entry": O.at[mon, s], "last_close": np.nan, "liq": False,
                "fund": 0.0, "pnl": 0.0} for s, wt in w.items()}
    for k in range(7):
        d = mon + k * DAY
        d_end = d + DAY
        for s, p in port.items():
            # funding events in (d, d+1]
            f = FUND.get(s)
            if f is not None and not (FUND_STOP_ON_LIQ and p["liq"]):
                ev = f[(f.index > d) & (f.index <= d_end)]
                scale = 1.0
                if DRIFT and len(ev):
                    o_, c_ = O.at[d, s], C.at[d, s]
                    scale = ((o_ + c_) / 2 / p["entry"]) if pd.notna(o_) and pd.notna(c_) else \
                        (p["last_close"] / p["entry"] if pd.notna(p["last_close"]) else 1.0)
                for rate in ev.values:
                    p["fund"] += -p["w"] * rate * scale
            if d in dates and pd.notna(C.at[d, s]):
                p["last_close"] = C.at[d, s]
            # daily liquidation check for shorts (high >= 2x entry)
            if p["w"] < 0 and not p["liq"] and d in dates and pd.notna(H.at[d, s]) \
                    and H.at[d, s] >= 2 * p["entry"]:
                p["liq"] = True
    out = {}
    for s, p in port.items():
        if p["liq"]:
            r = -1.0; px = np.nan; how = "liq"
        else:
            px = O.at[nxt, s] if nxt in dates else np.nan
            how = "open"
            if pd.isna(px):
                px = p["last_close"]; how = "lastclose"
            r = np.sign(p["w"]) * (px / p["entry"] - 1)
        p["pnl"] = abs(p["w"]) * r
        out[s] = dict(w=p["w"], entry=p["entry"], exit=px, how=how, ret_raw=px / p["entry"] - 1
                      if pd.notna(px) else np.nan, pnl=p["pnl"], fund=p["fund"])
    return out


rows, detail = [], {}
w_prev = {}
mon = pd.Timestamp("2023-01-02")
last_mon = pd.Timestamp("2026-09-21")
while mon <= last_mon:
    sel = select(mon)
    if sel is None:
        print("skip", mon.date())
        mon += 7 * DAY
        continue
    w, sc = sel
    syms = set(w) | set(w_prev)
    turn = sum(abs(w.get(s, 0) - w_prev.get(s, 0)) for s in syms)
    res = hold_week(mon, w)
    gross = sum(v["pnl"] for v in res.values())
    fsum = sum(v["fund"] for v in res.values())
    cost = FEE * turn
    rows.append(dict(week=mon.date(), gross=gross, funding=fsum, cost=cost, net=gross + fsum - cost))
    detail[str(mon.date())] = {s: {**{k: (float(v) if isinstance(v, (float, np.floating)) else v)
                                      for k, v in res[s].items()}, "score": sc[s]} for s in res}
    w_prev = w
    mon += 7 * DAY

R = pd.DataFrame(rows)
R["week"] = pd.to_datetime(R["week"])
tag = ("_drift" if DRIFT else "") + ("_qvnan" if QV_ZERO_AS_NAN else "") + ("_fundstop" if FUND_STOP_ON_LIQ else "")
R.to_csv(HERE / f"weekly{tag}.csv", index=False)
json.dump(detail, open(HERE / f"detail{tag}.json", "w"), indent=0, default=str)


def summ(x):
    return dict(n=len(x), net_ann=x.net.mean() * 52, gross_ann=x.gross.mean() * 52,
                funding_ann=x.funding.mean() * 52, cost_ann=x.cost.mean() * 52,
                gross_plus_fund_ann=(x.gross + x.funding).mean() * 52)


ho = R[(R.week >= "2025-10-01") & (R.week <= "2026-09-21")]
ins = R[(R.week >= "2023-01-01") & (R.week < "2025-09-30")]
print("HOLDOUT", {k: round(v, 4) for k, v in summ(ho).items()})
print("INSAMPLE", {k: round(v, 4) for k, v in summ(ins).items()})
print("liquidations:", sum(v["how"] == "liq" for d in detail.values() for v in d.values()),
      "lastclose exits:", sum(v["how"] == "lastclose" for d in detail.values() for v in d.values()))
top = ho.sort_values("net", ascending=False).head(3)
for _, r in top.iterrows():
    k = str(r.week.date())
    print(k, f"net={r.net:.4f} gross={r.gross:.4f} fund={r.funding:.4f}")
    for s, v in sorted(detail[k].items(), key=lambda kv: -kv[1]["w"]):
        print(f"   {'L' if v['w']>0 else 'S'} {s:14s} ret={v['ret_raw']:+.3f} pnl={v['pnl']:+.4f} fund={v['fund']:+.4f} {v['how']}")
