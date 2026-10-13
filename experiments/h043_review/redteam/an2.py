import numpy as np, pandas as pd
u = pd.read_csv("universe_weeks.csv.gz", parse_dates=["week"])
fd = pd.read_csv("fd.csv.gz", index_col=0, parse_dates=True)
c = pd.read_csv("c.csv.gz", index_col=0, parse_dates=True)
u["f"] = u.fsum.fillna(0.0)
u["rliq"] = np.where(u.hmax_ratio >= 2, 1.0, u.r)
u["L"] = u.r - u.f            # long unit return
u["S"] = -u.rliq + u.f        # short unit return
# prior-week funding and prior 7d vol
fprev, vol = {}, {}
lr = np.log(c).diff()
for w in u.week.unique():
    sun = w - pd.Timedelta("1D")
    fprev[w] = fd.loc[sun - pd.Timedelta("6D"):sun].sum()
    vol[w] = lr.loc[sun - pd.Timedelta("29D"):sun].std()
u["fprev"] = [fprev[w].get(s, 0.0) for w, s in zip(u.week, u.sym)]
u["vol30d"] = [vol[w].get(s, np.nan) for w, s in zip(u.week, u.sym)]
u["mom1"] = u.mom1.fillna(0.0); u["vol30d"] = u.groupby("week").vol30d.transform(lambda x: x.fillna(x.median()))
u.to_csv("u2.csv.gz", index=False)
HO = pd.Timestamp("2025-10-01", tz="UTC"); S = pd.Timestamp("2023-01-01", tz="UTC")
def strat(df, col, n=5, cost=True):
    out = {}
    prev = {}
    for w, g in df.groupby("week"):
        g = g.dropna(subset=[col]).sort_values([col, "sym"])
        bot, top = g.iloc[:n], g.iloc[-n:]
        gross = 0.1 * (top.L.sum() + bot.S.sum())
        new = {**{s: 0.1 for s in top.sym}, **{s: -0.1 for s in bot.sym}}
        to = sum(abs(new.get(k, 0) - prev.get(k, 0)) for k in set(new) | set(prev))
        prev = new
        out[w] = gross - (to * 0.0015 if cost else 0)
    return pd.Series(out)
def rep(r, tag):
    o = r[(r.index >= S) & (r.index < HO)]; h = r[r.index >= HO]
    print(f"{tag:28s} OOS ann {o.mean()*52:7.3f} sh {o.mean()/o.std()*52**.5:5.2f} | HO ann {h.mean()*52:7.3f} sh {h.mean()/h.std()*52**.5:5.2f}")
    return r
base = rep(strat(u, "score"), "taker ratio (base)")
u = u.dropna(subset=["score"])
mom = rep(strat(u, "mom1"), "1w momentum")
fc = u.assign(nf=-u.fprev); rep(strat(fc, "nf"), "neg prior funding (H008-like)")
# correlations
cs = u.groupby("week").apply(lambda g: pd.Series({"rho_mom": g.score.rank().corr(g.mom1.rank()),
                                                   "rho_negf": g.score.rank().corr((-g.fprev).rank()),
                                                   "rho_vol": g.score.rank().corr(g.vol30d.rank())}))
print("mean XS rank corr score vs:", cs.mean().round(3).to_dict())
# overlap of long legs
def legs(df, col):
    d = {}
    for w, g in df.groupby("week"):
        g = g.dropna(subset=[col]).sort_values([col, "sym"]); d[w] = (set(g.sym.iloc[-5:]), set(g.sym.iloc[:5]))
    return d
lb, lm = legs(u, "score"), legs(u, "mom1")
print("avg long overlap with mom", np.mean([len(lb[w][0] & lm[w][0]) for w in lb]), "short overlap", np.mean([len(lb[w][1] & lm[w][1]) for w in lb]))
# residualized score: XS OLS of score rank on ranks of mom1, -fprev, vol
def resid(g):
    X = np.c_[np.ones(len(g)), g.mom1.rank(), (-g.fprev).rank(), g.vol30d.rank().fillna(len(g)/2)]
    y = g.score.rank().to_numpy()
    b = np.linalg.lstsq(X, y, rcond=None)[0]
    return pd.Series(y - X @ b, index=g.index)
u["res_all"] = u.groupby("week", group_keys=False).apply(resid)
def resid_m(g):
    X = np.c_[np.ones(len(g)), g.mom1.rank()]
    y = g.score.rank().to_numpy(); b = np.linalg.lstsq(X, y, rcond=None)[0]
    return pd.Series(y - X @ b, index=g.index)
u["res_m"] = u.groupby("week", group_keys=False).apply(resid_m)
rep(strat(u, "res_m"), "score resid on mom")
rep(strat(u, "res_all"), "score resid on mom,fund,vol")
rep(strat(u, "score", cost=False), "base gross")
# stratified permutation: permute score within buckets of mom1 (5 buckets of ~10), and within buckets of fprev
rng = np.random.default_rng(1)
def strat_fast(weeks, P=500, key=None):
    # weeks: list of (L, S, score, bucket) arrays; returns (P, nweeks) gross (no cost)
    out = np.zeros((P, len(weeks)))
    for t, (Lr, Sr, sc, bk) in enumerate(weeks):
        n = len(sc)
        scp = np.tile(sc, (P, 1))
        if bk is not None:
            for b in np.unique(bk):
                idx = np.where(bk == b)[0]
                perm = np.argsort(rng.random((P, len(idx))), axis=1)
                scp[:, idx] = sc[idx][perm]
        else:
            scp = sc[np.argsort(rng.random((P, n)), axis=1)]
        order = np.argsort(scp, axis=1, kind="stable")
        out[:, t] = 0.1 * (Lr[order[:, -5:]].sum(1) + Sr[order[:, :5]].sum(1))
    return out
for bucket_col in ("none", "mom1", "fprev", "vol30d"):
    for period, (a, b) in {"OOS": (S, HO), "HO": (HO, pd.Timestamp("2027-01-01", tz="UTC"))}.items():
        sub = u[(u.week >= a) & (u.week < b)]
        weeks, real = [], []
        for w, g in sub.groupby("week"):
            g = g.dropna(subset=["score"]).sort_values("sym")
            bk = None if bucket_col == "none" else pd.qcut(g[bucket_col].rank(method="first"), 10, labels=False).to_numpy()
            weeks.append((g.L.to_numpy(), g.S.to_numpy(), g.score.to_numpy(), bk))
            gg = g.sort_values(["score", "sym"])
            real.append(0.1 * (gg.L.iloc[-5:].sum() + gg.S.iloc[:5].sum()))
        null = strat_fast(weeks, P=1000).mean(1); rm = np.mean(real)
        print(f"perm within deciles of {bucket_col:7s} {period}: real gross ann {rm*52:.3f} null mean {null.mean()*52:.3f} p95 {np.quantile(null,.95)*52:.3f} p={(1+(null>=rm).sum())/1001:.4f}")
