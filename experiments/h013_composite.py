"""H013 · G2/G3: ranking compuesto de señales débiles con reentreno walk-forward.

Uso: python3 experiments/h013_composite.py [g3]
Diseño fijado en HYPOTHESES.md. Modelos: ridge (λ=1) y suma con signo de IC.
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
import h005_xs_momentum as h5  # noqa: E402
from h008_funding_xs import funding_events  # noqa: E402
from src import metrics  # noqa: E402

FEATS = ["r1", "r4", "fund7", "vratio", "vol30"]
HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")
G2_EDGES = [pd.Timestamp(x, tz="UTC") for x in ("2021-01-01", "2021-07-01", "2022-01-01",
                                                  "2022-07-01", "2023-01-01")]
G3_EDGES = sorted(set(list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT,
                                          freq="6MS")) + [HOLDOUT]))
LAMBDA = 1.0


def build_features(o, c, qv, ev, end):
    """Filas (lunes, símbolo) del universo del motor, con características y etiqueta."""
    mondays = o.index[(o.index.dayofweek == 0) & (o.index < end)]
    first = o.apply(lambda s: s.first_valid_index())
    vol30 = qv.rolling(30, min_periods=20).sum()
    lr = np.log(c).diff()
    rows = []
    for i, mon in enumerate(mondays[:-1]):
        sun, nxt = mon - pd.Timedelta("1D"), mondays[i + 1]
        if sun - pd.Timedelta("35D") not in c.index:
            continue
        alive = o.loc[mon].notna() & (first <= sun - pd.Timedelta("90D"))
        names = vol30.loc[sun][alive].nlargest(50).index
        week = o.loc[mon:nxt].index[:-1]
        for s in names:
            f = ev.get(s)
            fw = f[(f.index >= mon - pd.Timedelta("7D")) & (f.index < mon)] if f is not None else []
            p1 = o.loc[nxt, s]
            if np.isnan(p1):
                seg = c.loc[week, s].dropna()
                p1 = seg.iloc[-1] if len(seg) else np.nan
            fwk = f[(f.index > mon) & (f.index <= nxt)].sum() if f is not None else 0.0
            prev = qv.loc[sun - pd.Timedelta("34D"):sun - pd.Timedelta("7D"), s].sum() / 4
            rows.append({
                "mon": mon, "sym": s,
                "r1": c.loc[sun, s] / c.loc[sun - pd.Timedelta("7D"), s] - 1,
                "r4": c.loc[sun, s] / c.loc[sun - pd.Timedelta("28D"), s] - 1,
                "fund7": (fw.sum() / 21) if len(fw) else np.nan,
                "vratio": qv.loc[sun - pd.Timedelta("6D"):sun, s].sum() / prev if prev > 0 else np.nan,
                "vol30": lr.loc[sun - pd.Timedelta("29D"):sun, s].std(),
                "y": p1 / o.loc[mon, s] - 1 - fwk})
    df = pd.DataFrame(rows)
    for k in FEATS + ["y"]:
        df[k + "_p"] = df.groupby("mon")[k].rank(pct=True) - 0.5
    return df.fillna({k + "_p": 0.0 for k in FEATS})


def fit_predict(train, test, model):
    X = train[[f + "_p" for f in FEATS]].to_numpy()
    Xt = test[[f + "_p" for f in FEATS]].to_numpy()
    y = train["y_p"].fillna(0).to_numpy()
    if model == "ridge":
        beta = np.linalg.solve(X.T @ X + LAMBDA * np.eye(X.shape[1]), X.T @ y)
    else:   # signo de la IC media semanal de cada característica
        ic = train.groupby("mon").apply(
            lambda g: pd.Series({f: np.corrcoef(g[f + "_p"], g["y_p"].fillna(0))[0, 1]
                                 for f in FEATS}), include_groups=False).mean()
        beta = np.sign(ic.fillna(0).to_numpy())
    return pd.Series(Xt @ beta, index=test.index), beta


def run_model(o, c, h, qv, fd, df, edges, model, end):
    preds, betas = {}, {}
    for a, b in zip(edges[:-1], edges[1:]):
        tr = df[df["mon"] < a - pd.Timedelta("7D")]
        te = df[(df["mon"] >= a) & (df["mon"] < b)]
        if len(te) == 0:
            continue
        p, beta = fit_predict(tr, te, model)
        betas[str(a.date())] = [round(float(x), 4) for x in beta]
        for (mon, sym), v in zip(zip(te["mon"], te["sym"]), p):
            preds.setdefault(mon, {})[sym] = v

    def score(sun, mon, names):
        d = preds.get(mon, {})
        return pd.Series({s: d[s] for s in names if s in d}, dtype=float)

    r = h5.run(o, c, h, qv, fd, 1, "mom", end=end, score_fn=score)
    r = r[r.index >= edges[0]]
    return r, betas


def main(g3=False):
    o, c, h, qv, fd = h5.panel()
    ev = funding_events(o.columns)
    edges = G3_EDGES if g3 else G2_EDGES
    end = edges[-1]
    df = build_features(o, c, qv, ev, end + pd.Timedelta("8D"))
    df = df[df["mon"] < end]
    res = {}
    for model in ("ridge", "icsign"):
        r, betas = run_model(o, c, h, qv, fd, df, edges, model, end)
        lo, hi = metrics.block_bootstrap_mean_ci(r["net"].to_numpy(), block=8, n_boot=5000)
        res[model] = {"weeks": int(len(r)), "ann": float(r["net"].mean() * 52),
                      "sharpe_m": metrics.sharpe_resampled(r["net"]),
                      "max_dd": metrics.max_drawdown(r["net"].to_numpy()),
                      "ci95_weekly": [lo, hi], "betas": betas, "features": FEATS,
                      "yearly": {int(y): float(v) for y, v in
                                 r["net"].groupby(r.index.year).sum().items()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    name = "h013_g3.json" if g3 else "h013_g2.json"
    (ROOT / "reports" / name).write_text(json.dumps({"commit": commit, "variants": 2,
                                                     "results": res}, indent=1) + "\n")
    print(json.dumps({k: {x: v[x] for x in ("weeks", "ann", "sharpe_m", "max_dd",
                                            "ci95_weekly", "yearly")} for k, v in res.items()},
                     indent=1))


if __name__ == "__main__":
    main(g3=len(sys.argv) > 1 and sys.argv[1] == "g3")
