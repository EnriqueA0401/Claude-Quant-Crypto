import numpy as np, pandas as pd
u = pd.read_csv("u2.csv.gz", parse_dates=["week"]).dropna(subset=["score"])
o = pd.read_csv("o.csv.gz", index_col=0, parse_dates=True); c = pd.read_csv("c.csv.gz", index_col=0, parse_dates=True)
h = pd.read_csv("h.csv.gz", index_col=0, parse_dates=True); fd = pd.read_csv("fd.csv.gz", index_col=0, parse_dates=True)
HO = pd.Timestamp("2025-10-01", tz="UTC"); S = pd.Timestamp("2023-01-01", tz="UTC")
def legs(df, col):
    d = {}
    for w, g in df.groupby("week"):
        g = g.dropna(subset=[col]).sort_values([col, "sym"]); d[w] = (list(g.sym.iloc[-5:]), list(g.sym.iloc[:5]))
    return d
def run_delay(lg, delay):
    out, prev = {}, {}
    for w, (lo, sh) in lg.items():
        a, b = w + pd.Timedelta(days=delay), w + pd.Timedelta(days=7 + delay)
        days = o.loc[a:b].index[:-1]
        g = 0.0
        for s, sg in [(x, 1) for x in lo] + [(x, -1) for x in sh]:
            seg = o.loc[days, s].dropna()
            if seg.empty: continue
            p0 = seg.iloc[0]; p1 = o.loc[b, s] if b in o.index else np.nan
            if np.isnan(p1): p1 = c.loc[days, s].dropna().iloc[-1]
            r = p1 / p0 - 1
            if sg < 0 and h.loc[days, s].max() >= 2 * p0: r = 1.0
            f = fd.loc[days, s].sum() if s in fd.columns else 0
            g += 0.1 * sg * (r - f)
        new = {**{s: .1 for s in lo}, **{s: -.1 for s in sh}}
        to = sum(abs(new.get(k, 0) - prev.get(k, 0)) for k in set(new) | set(prev)); prev = new
        out[w] = g - to * 0.0015
    return pd.Series(out)
def rep(r, tag):
    o_ = r[(r.index >= S) & (r.index < HO)]; h_ = r[r.index >= HO]
    print(f"{tag:34s} OOS ann {o_.mean()*52:7.3f} sh {o_.mean()/o_.std()*52**.5:5.2f} | HO ann {h_.mean()*52:7.3f} sh {h_.mean()/h_.std()*52**.5:5.2f}")
lg = legs(u, "score")
for d in (0, 1, 2):
    rep(run_delay(lg, d), f"base, entry delayed {d}d")
lm = legs(u, "mom1")
rep(run_delay(lm, 1), "1w momentum, delayed 1d")
# symbol persistence of score
piv = u.pivot_table(index="week", columns="sym", values="score")
rk = piv.rank(axis=1, pct=True)
ac = [rk[s].dropna().autocorr(1) for s in rk.columns if rk[s].notna().sum() > 20]
print("median weekly autocorr of score pct-rank by symbol:", np.nanmedian(ac).round(3))
# symbol fixed effect share
m = u.assign(pr=u.groupby("week").score.rank(pct=True))
fe = m.groupby("sym").pr.transform("mean")
print("R2 of symbol FE on pct-rank:", round(1 - ((m.pr - fe) ** 2).sum() / ((m.pr - m.pr.mean()) ** 2).sum(), 3))
# demeaned score: minus own trailing 8-week mean (past only)
piv8 = piv.rolling(8, min_periods=4).mean().shift(1)
dm = (piv - piv8).stack().rename("dm").reset_index()
u2 = u.merge(dm, on=["week", "sym"], how="left")
rep(run_delay(legs(u2, "dm"), 0), "score minus own 8w mean")
# weekly stats in holdout
wk = pd.read_csv("wk.csv", index_col=0, parse_dates=True)
ho = wk.net[wk.index >= HO]; oo = wk.net[(wk.index >= S) & (wk.index < HO)]
for n, r in (("OOS", oo), ("HO", ho)):
    print(n, "t-stat", round(r.mean() / r.std() * len(r) ** .5, 2), "skew", round(r.skew(), 2), "frac weeks>0", round((r > 0).mean(), 2),
          "worst week", round(r.min(), 3), "best", round(r.max(), 3))
# drawdown path
eq = (1 + ho).cumprod(); print("HO compounding equity end", round(eq.iloc[-1], 3), "maxDD compounding", round((eq / eq.cummax() - 1).min(), 3))
eq = (1 + oo).cumprod(); print("OOS compounding maxDD", round((eq / eq.cummax() - 1).min(), 3))
