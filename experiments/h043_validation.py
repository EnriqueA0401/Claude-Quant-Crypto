"""H043 · validación complementaria pre-registrada: permutación y holdout.

Uso: python3 experiments/h043_validation.py
(a) Permutación 2023-01 → 2025-09: cada semana se reasignan al azar las puntuaciones entre
    los mismos pares elegibles (misma permutación para las 4 variantes). Retornos, funding,
    liquidaciones y costes son los reales: solo se destruye la información de la señal.
(b) Holdout 2025-10-01 → 2026-09-30, variante cont_7d, una sola vez.
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
from h043_g4 import score_w  # noqa: E402
from h043_taker_flow import HOLDOUT, make_score, stats, taker_panel  # noqa: E402

START = pd.Timestamp("2023-01-01", tz="UTC")
HOLDOUT_END = pd.Timestamp("2026-09-30", tz="UTC")
N_PERM, SEED = 2000, 0


def week_table(o, c, h, qv, fd, end, score_fns):
    """Por semana: pares elegibles, retorno por par si largo / si corto (con funding y
    liquidación, igual que h5.run) y el orden ascendente de cada variante."""
    cols = list(o.columns)
    pos = {s: i for i, s in enumerate(cols)}
    mondays = o.index[o.index.dayofweek == 0]
    mondays = mondays[mondays < end]
    first = o.apply(lambda s: s.first_valid_index())
    vol30 = qv.rolling(30, min_periods=20).sum()
    weeks = []
    for i, mon in enumerate(mondays[:-1]):
        sun, nxt = mon - pd.Timedelta("1D"), mondays[i + 1]
        if sun - pd.Timedelta(weeks=1) not in c.index or sun not in c.index:
            continue
        alive = o.loc[mon].notna() & (first <= sun - pd.Timedelta("90D"))
        liquid = vol30.loc[sun][alive].nlargest(50).index
        scores = {k: f(sun, mon, liquid) for k, f in score_fns.items()}
        names = None
        for s in scores.values():                      # mismos pares válidos en todas
            v = set(s.dropna().index)
            names = v if names is None else names & v
        names = sorted(names)
        if len(names) < 2 * h5.N_SIDE or any(len(s.dropna()) < 2 * h5.N_SIDE for s in scores.values()):
            continue
        week = o.loc[mon:nxt].index[:-1]
        rl, rs = [], []
        for s in names:
            p0 = o.loc[week, s].dropna().iloc[0]
            p1 = o.loc[nxt, s]
            if np.isnan(p1):
                p1 = c.loc[week, s].dropna().iloc[-1]
            r = p1 / p0 - 1
            rliq = 1.0 if h.loc[week, s].max() >= 2 * p0 else r
            fsum = fd.loc[week, s].sum() if s in fd.columns else 0.0
            rl.append(r - fsum)
            rs.append(-rliq + fsum)
        orders = {}
        for k, s in scores.items():
            ranked = h5._rank(s[names])
            orders[k] = np.array([names.index(x) for x in ranked.index])
        weeks.append({"week": mon, "cols": np.array([pos[s] for s in names]),
                      "rl": np.array(rl), "rs": np.array(rs), "orders": orders})
    return weeks, len(cols)


def simulate(weeks, ncols, variant, perms):
    """perms: lista (una por semana) de matrices (P, n) con permutaciones de posiciones
    locales; la identidad reproduce la estrategia real. Devuelve (P, semanas) de netos."""
    P = perms[0].shape[0]
    prev = np.zeros((P, ncols))
    out = np.zeros((P, len(weeks)))
    rows = np.arange(P)[:, None]
    for t, wk in enumerate(weeks):
        order = wk["orders"][variant]
        top, bot = order[-h5.N_SIDE:], order[:h5.N_SIDE]
        lng, sht = perms[t][:, top], perms[t][:, bot]  # posiciones locales tras permutar
        gross = h5.W * (wk["rl"][lng].sum(1) + wk["rs"][sht].sum(1))
        new = np.zeros((P, ncols))
        new[rows, wk["cols"][lng]] = h5.W
        new[rows, wk["cols"][sht]] = -h5.W
        cost = np.abs(new - prev).sum(1) * h5.PER_SIDE
        prev = new
        out[:, t] = gross - cost
    return out


def main():
    o, c, h, qv, fd = h5.panel()
    tb = taker_panel(o.columns).reindex(o.index)
    fams = {"cont_7d": score_w(tb, qv, 7), "cont_3d": score_w(tb, qv, 3),
            "cont_14d": score_w(tb, qv, 14), "rev_7d": make_score(tb, qv, -1.0)}
    end_g3 = o.index[(o.index.dayofweek == 0) & (o.index <= HOLDOUT)][-1] + pd.Timedelta("1D")
    weeks, ncols = week_table(o, c, h, qv, fd, end_g3, fams)
    weeks = [w for w in weeks if w["week"] >= START - pd.Timedelta("7D")]
    # la primera semana solo fija las posiciones previas (turnover), como en h5.run
    rng = np.random.default_rng(SEED)
    ident = [np.arange(len(w["rl"]))[None, :] for w in weeks]
    perms = [np.argsort(rng.random((N_PERM, len(w["rl"]))), axis=1) for w in weeks]
    keep = np.array([w["week"] >= START for w in weeks])
    real = {k: simulate(weeks, ncols, k, ident)[0][keep] for k in fams}
    null = {k: simulate(weeks, ncols, k, perms)[:, keep] for k in fams}

    # comprobación: la identidad reproduce h5.run exactamente
    ref = h5.run(o, c, h, qv, fd, 1, "mom", end=end_g3, score_fn=fams["cont_7d"])["net"]
    ref = ref[ref.index >= START].to_numpy()
    assert len(ref) == len(real["cont_7d"]) and np.allclose(ref, real["cont_7d"], atol=1e-12), \
        "el simulador no reproduce h5.run"

    mu_real = {k: float(v.mean()) for k, v in real.items()}
    mu_null = {k: v.mean(1) for k, v in null.items()}
    fam_null = np.max(np.column_stack(list(mu_null.values())), axis=1)
    fam_real = max(mu_real.values())
    perm = {"n_perm": N_PERM, "seed": SEED, "weeks": int(keep.sum()),
            "mean_weekly_real": mu_real,
            "null_mean_weekly": {k: float(v.mean()) for k, v in mu_null.items()},
            "null_p95_weekly": {k: float(np.quantile(v, 0.95)) for k, v in mu_null.items()},
            "p_single_cont_7d": float((1 + (mu_null["cont_7d"] >= mu_real["cont_7d"]).sum()) / (1 + N_PERM)),
            "p_family": float((1 + (fam_null >= fam_real).sum()) / (1 + N_PERM))}

    # (b) holdout: una sola ejecución de cont_7d
    end_ho = HOLDOUT_END - pd.Timedelta("1D")          # último lunes terminal: 2026-09-28
    hr = h5.run(o, c, h, qv, fd, 1, "mom", end=end_ho, score_fn=fams["cont_7d"])
    ho = hr["net"][hr.index >= HOLDOUT]
    hw, hn = week_table(o, c, h, qv, fd, end_ho, {"cont_7d": fams["cont_7d"]})
    hw = [w for w in hw if w["week"] >= HOLDOUT - pd.Timedelta("7D")]
    hk = np.array([w["week"] >= HOLDOUT for w in hw])
    rng2 = np.random.default_rng(SEED + 1)
    hp = [np.argsort(rng2.random((N_PERM, len(w["rl"]))), axis=1) for w in hw]
    hnull = simulate(hw, hn, "cont_7d", hp)[:, hk].mean(1)
    holdout = {"stats": stats(ho), "first_week": str(ho.index[0].date()),
               "last_week": str(ho.index[-1].date()),
               "gross_ann": float(hr["gross"][hr.index >= HOLDOUT].mean() * 52),
               "cost_ann": float(hr["cost"][hr.index >= HOLDOUT].mean() * 52),
               "null_mean_ann": float(hnull.mean() * 52),
               "p_perm_holdout": float((1 + (hnull >= ho.mean()).sum()) / (1 + N_PERM))}
    holdout["pass"] = bool(holdout["stats"]["ann"] > 0.045 and ho.mean() > hnull.mean())
    perm["pass"] = perm["p_family"] < 0.05

    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    res = {"commit": commit, "permutation": perm, "holdout": holdout}
    (ROOT / "reports/h043_validation.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({"perm": {k: perm[k] for k in ("mean_weekly_real", "null_p95_weekly",
                                                    "p_single_cont_7d", "p_family", "pass")},
                      "holdout": {k: holdout[k] for k in ("first_week", "last_week", "gross_ann",
                                                          "cost_ann", "null_mean_ann",
                                                          "p_perm_holdout", "pass")},
                      "holdout_ann": holdout["stats"]["ann"],
                      "holdout_sharpe_m": holdout["stats"]["sharpe_m"],
                      "holdout_dd": holdout["stats"]["max_dd"]}, indent=1))


if __name__ == "__main__":
    main()
