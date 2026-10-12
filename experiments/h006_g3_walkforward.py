"""H006 · G3: walk-forward por fecha de listado (desarrollo 2020-01 → 2025-09).

Uso: python3 experiments/h006_g3_walkforward.py
Regla de selección fijada antes de ver OOS: en cada fold, la variante con mayor t
(media / error estándar con bootstrap por meses) en los listados del train.
Folds de test de 6 meses desde 2023-01; purga: un evento de train solo cuenta si su
ventana (≤ 30 días) termina antes del test (embargo de 31 días sobre la fecha de listado).
Holdout: listados desde 2025-10-01 y ventanas que lleguen allí: excluidos.
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
from h006_listing import collect_events  # noqa: E402

HOLDOUT = pd.Timestamp("2025-10-01", tz="UTC")


def cluster_t(g, rng, n=2000):
    by_m = g.groupby(pd.to_datetime(g["listed"]).dt.to_period("M"))["net"].apply(list)
    boots = [np.mean(np.concatenate([by_m.iloc[i] for i in rng.integers(0, len(by_m), len(by_m))]))
             for _ in range(n)]
    return g["net"].mean() / np.std(boots), np.quantile(boots, [0.025, 0.975])


def main():
    ev = collect_events(pd.Timestamp("2020-01-02", tz="UTC"), HOLDOUT, data_end=HOLDOUT)
    ev["listed_ts"] = pd.to_datetime(ev["listed"]).dt.tz_localize("UTC")
    ev["var"] = ev["E"].astype(str) + "|" + ev["N"].astype(str) + "|" + ev["stop"].astype(str)
    ev.to_csv(ROOT / "reports/h006_events_dev.csv", index=False)
    rng = np.random.default_rng(0)
    edges = list(pd.date_range(pd.Timestamp("2023-01-01", tz="UTC"), HOLDOUT, freq="6MS")) + [HOLDOUT]
    edges = sorted(set(edges))
    oos, folds = [], []
    for a, b in zip(edges[:-1], edges[1:]):
        tr = ev[ev["listed_ts"] < a - pd.Timedelta("31D")]
        te = ev[(ev["listed_ts"] >= a) & (ev["listed_ts"] < b)]
        score = {v: cluster_t(g, rng, 500)[0] for v, g in tr.groupby("var")}
        best = max(score, key=score.get)
        g = te[te["var"] == best]
        oos.append(g)
        folds.append({"test": f"{a.date()}..{b.date()}", "chosen": best,
                      "train_t": float(score[best]), "events": int(len(g)),
                      "mean_net": float(g["net"].mean()) if len(g) else None,
                      "median_net": float(g["net"].median()) if len(g) else None})
    O = pd.concat(oos)
    t, ci = cluster_t(O, rng, 5000)
    yearly = O.groupby(O["listed_ts"].dt.year)["net"].agg(["mean", "count"])
    summ = {"oos_events": int(len(O)), "oos_mean_net": float(O["net"].mean()),
            "oos_median_net": float(O["net"].median()), "oos_hit": float((O["net"] > 0).mean()),
            "oos_t_cluster": float(t), "oos_ci95_cluster_month": [float(ci[0]), float(ci[1])],
            "oos_mean_minus_btc_short": float((O["net"] - O["btc_short"]).dropna().mean()),
            "oos_liquidations": int(O["liquidated"].sum()),
            "yearly": {int(y): {"mean": float(r["mean"]), "n": int(r["count"])}
                       for y, r in yearly.iterrows()}}
    commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                            cwd=ROOT).stdout.strip()
    (ROOT / "reports/h006_g3.json").write_text(json.dumps(
        {"commit": commit, "folds": folds, "summary": summ}, indent=1) + "\n")
    print(pd.DataFrame(folds).to_string())
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
