"""Instrumented copy of h5.run for cont_7d: per-position records 2022-12 -> 2026-09."""
import sys
sys.path.insert(0, "/home/user/Claude-Quant-Crypto"); sys.path.insert(0, "/home/user/Claude-Quant-Crypto/experiments")
import numpy as np, pandas as pd
import h005_xs_momentum as h5
from h043_taker_flow import taker_panel
OUT = "/tmp/claude-0/-home-user-Claude-Quant-Crypto/d19d4462-a4d1-5a19-968f-d7ab82638a9c/scratchpad/redteam/"
o, c, h, qv, fd = h5.panel()
tb = taker_panel(o.columns).reindex(o.index)
# save panels as parquet/csv for reuse (scratch only)
for n, df in dict(o=o, c=c, h=h, qv=qv, fd=fd, tb=tb).items():
    df.to_csv(OUT + f"{n}.csv.gz")
mondays = o.index[o.index.dayofweek == 0]
mondays = mondays[(mondays >= pd.Timestamp("2022-12-26", tz="UTC")) & (mondays < pd.Timestamp("2026-09-29", tz="UTC"))]
first = o.apply(lambda s: s.first_valid_index())
vol30 = qv.rolling(30, min_periods=20).sum()
rows, uni = [], []
for i, mon in enumerate(mondays[:-1]):
    sun, nxt = mon - pd.Timedelta("1D"), mondays[i + 1]
    alive = o.loc[mon].notna() & (first <= sun - pd.Timedelta("90D"))
    liquid = vol30.loc[sun][alive].nlargest(50).index
    a = tb.loc[sun - pd.Timedelta("6D"):sun, liquid].sum(min_count=5)
    b = qv.loc[sun - pd.Timedelta("6D"):sun, liquid].sum(min_count=5)
    sc = (a / b).dropna()
    mom1 = c.loc[sun, liquid] / c.loc[sun - pd.Timedelta("7D"), liquid] - 1
    week = o.loc[mon:nxt].index[:-1]
    ranked = h5._rank(sc)
    top, bot = list(ranked.index[-5:]), list(ranked.index[:5])
    for s in sc.index:
        seg = o.loc[week, s].dropna()
        p0 = seg.iloc[0]; p1 = o.loc[nxt, s]
        if np.isnan(p1): p1 = c.loc[week, s].dropna().iloc[-1]
        r = p1 / p0 - 1
        hmax = h.loc[week, s].max()
        fsum = fd.loc[week, s].sum() if s in fd.columns else np.nan
        side = 1 if s in top else (-1 if s in bot else 0)
        uni.append(dict(week=mon, sym=s, score=sc[s], mom1=mom1.get(s, np.nan), r=r, hmax_ratio=hmax / p0,
                        fsum=fsum, has_f=s in fd.columns, side=side, vol30=vol30.loc[sun, s],
                        qv_mon=qv.loc[mon, s], qv_sun=qv.loc[sun, s]))
pd.DataFrame(uni).to_csv(OUT + "universe_weeks.csv.gz", index=False)
print("done")
