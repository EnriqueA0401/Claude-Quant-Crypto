import numpy as np, pandas as pd
u = pd.read_csv("universe_weeks.csv.gz", parse_dates=["week"])
u["f"] = u.fsum.fillna(0.0)
u["rliq"] = np.where(u.hmax_ratio >= 2, 1.0, u.r)
u["pnl_px"] = np.where(u.side == 1, 0.1 * u.r, np.where(u.side == -1, -0.1 * u.rliq, 0))
u["pnl_f"] = np.where(u.side == 1, -0.1 * u.f, np.where(u.side == -1, 0.1 * u.f, 0))
u["pnl"] = u.pnl_px + u.pnl_f
def cost(df):
    W = df[df.side != 0].pivot_table(index="week", columns="sym", values="side", aggfunc="sum").fillna(0) * 0.1
    W = W.reindex(sorted(df.week.unique())).fillna(0)
    return (W.diff().abs().sum(1)).fillna(W.abs().sum(1)) * 0.0015
pos = u[u.side != 0]
wk = pos.groupby("week")[["pnl", "pnl_px", "pnl_f"]].sum()
wk["cost"] = cost(u); wk["net"] = wk.pnl - wk.cost
HO = pd.Timestamp("2025-10-01", tz="UTC"); S = pd.Timestamp("2023-01-01", tz="UTC")
def summ(r, tag):
    print(f"{tag}: n={len(r)} ann={r.mean()*52:.3f} median={r.median():.4f} sharpe_w_ann={r.mean()/r.std()*52**.5:.2f}")
oos = wk[(wk.index >= S) & (wk.index < HO)]; ho = wk[wk.index >= HO]
for name, d in (("OOS", oos), ("HO", ho)):
    summ(d.net, name)
    print("  px ann", round(d.pnl_px.mean()*52, 3), "funding ann", round(d.pnl_f.mean()*52, 3), "cost", round(d.cost.mean()*52, 3))
    p = pos[(pos.week.isin(d.index))]
    print("  long px ann", round(p[p.side==1].pnl_px.sum()/len(d)*52,3), "short px ann", round(p[p.side==-1].pnl_px.sum()/len(d)*52,3),
          "long f", round(p[p.side==1].pnl_f.sum()/len(d)*52,3), "short f", round(p[p.side==-1].pnl_f.sum()/len(d)*52,3))
    print("  short liquidations", int(((p.side==-1)&(p.hmax_ratio>=2)).sum()), "positions w/o funding file", int((~p.has_f).sum()))
    # jackknife weeks
    s = d.net.sort_values(ascending=False)
    for k in (1, 3, 5, 10):
        print(f"  drop top{k} weeks ann={s.iloc[k:].mean()*52:.3f}", end=";")
    print()
    bysym = p.groupby("sym").pnl.sum().sort_values(ascending=False)
    print("  top syms", bysym.head(8).round(3).to_dict())
    print("  worst syms", bysym.tail(5).round(3).to_dict())
    for k in (1, 3, 5, 10):
        keep = ~p.sym.isin(bysym.index[:k])
        alt = p[keep].groupby("week").pnl.sum().reindex(d.index).fillna(0) - d.cost
        print(f"  drop top{k} syms ann={alt.mean()*52:.3f}", end=";")
    print()
    # top positions
    print(p.sort_values("pnl", ascending=False).head(8)[["week","sym","side","r","f","pnl","score","mom1","vol30"]].round(3).to_string())
    # fraction of long positions that were 1w momentum top-10
    print("  yearly", d.net.groupby(d.index.year).sum().round(3).to_dict())
wk.to_csv("wk.csv")
