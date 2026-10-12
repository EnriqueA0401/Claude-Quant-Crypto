"""H012 independent reimplementation (code-review protocol step 4).

Explicit event-driven broker loop for cash-and-carry with quarterly USDT-M
futures (long spot, short future), capital 1, each leg notional W=0.5.
Written without looking at src/carry.py or src/backtest.py.

Usage: python experiments/h012_independent.py
Output: reports/h012_independent.json
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data import load_klines  # noqa: E402

W = 0.5
ENTRY_COST = 0.0015 + 0.0010
EXIT_COST = 0.0025
REBAL_COST = 0.0025
REBAL_TRIGGER = 0.25
LIQ_MULT = 2 - 0.005
MIN_DAYS = 14.0
END = pd.Timestamp("2023-01-01", tz="UTC")
FUT_DIR = ROOT / "data" / "futures" / "um" / "monthly" / "klines"


def _utc(idx):
    idx = pd.DatetimeIndex(idx)
    return idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")


def load_inputs(asset, end):
    spot = load_klines("spot", asset)
    spot.index = _utc(spot.index)
    spot = spot[spot.index < end]
    # full hourly grid between first and last spot bar; spot ffilled
    idx = pd.date_range(spot.index[0], spot.index[-1], freq="1h", tz="UTC")
    spot = spot.reindex(idx)
    s_open = spot["open"].ffill().to_numpy(float)
    s_close = spot["close"].ffill().to_numpy(float)

    contracts = []
    for d in sorted(p.name for p in FUT_DIR.iterdir() if p.name.startswith(asset + "_")):
        f = load_klines("um", d)
        f.index = _utc(f.index)
        last = f.index[-1]
        if not last < end:
            continue
        fr = f.reindex(idx)  # no ffill for futures
        last_pos = idx.get_indexer([last])[0]
        contracts.append(dict(
            name=d, last=last, last_pos=int(last_pos),
            o=fr["open"].to_numpy(float), h=fr["high"].to_numpy(float),
            c=fr["close"].to_numpy(float)))
    return idx, s_open, s_close, contracts


def run(idx, s_open, s_close, contracts, theta, early):
    n = len(idx)
    times = idx
    pnl = np.zeros(n)          # per-bar net pnl
    stats = dict(entries=0, liquidations=0, rebalances=0, early_exits=0,
                 expiry_exits=0, costs=0.0, gross=0.0, nan_fopen_fallbacks=0,
                 skipped_entry_nan_fopen=0)
    pos = None                 # dict(k, F_ref, S_ref, prev_F1)
    pending_entry = None       # contract index
    pending_exit = False

    def days_to(k, i):
        return (contracts[k]["last"] - times[i]).total_seconds() / 86400.0

    for i in range(n - 1):     # last bar dropped
        # ---------- open of bar i: execute pending orders ----------
        if pending_exit:
            c = W * EXIT_COST
            pnl[i] -= c; stats["costs"] += c; stats["early_exits"] += 1
            pos = None; pending_exit = False
        elif pending_entry is not None:
            k = pending_entry; pending_entry = None
            fo = contracts[k]["o"][i]
            if np.isnan(fo):
                stats["skipped_entry_nan_fopen"] += 1
            else:
                c = W * ENTRY_COST
                pnl[i] -= c; stats["costs"] += c; stats["entries"] += 1
                pos = dict(k=k, F_ref=fo, S_ref=s_open[i], prev_F1=fo)
        # ---------- holding bar i: mark to open[i+1] ----------
        if pos is not None:
            ct = contracts[pos["k"]]
            F_ref, S_ref = pos["F_ref"], pos["S_ref"]
            f_o = ct["o"][i]
            if np.isnan(f_o):
                f_o = pos["prev_F1"]; stats["nan_fopen_fallbacks"] += 1
            ds = s_open[i + 1] - s_open[i]
            fh = ct["h"][i]
            if not np.isnan(fh) and fh >= F_ref * LIQ_MULT:
                bar = W * (min(ds, 2 * S_ref - s_open[i]) / S_ref
                           - (2 * F_ref - f_o) / F_ref)
                pnl[i] += bar; stats["gross"] += bar
                stats["liquidations"] += 1
                pos = None
            else:
                is_last = (i == ct["last_pos"])
                F1 = ct["c"][i] if is_last else ct["o"][i + 1]
                if np.isnan(F1):
                    F1 = f_o
                bar = W * (ds / S_ref - (F1 - f_o) / F_ref)
                pnl[i] += bar; stats["gross"] += bar
                pos["prev_F1"] = F1
                dev = abs(F1 / F_ref - 1)
                if dev > REBAL_TRIGGER:
                    c = W * dev * REBAL_COST
                    pnl[i] -= c; stats["costs"] += c; stats["rebalances"] += 1
                    pos["F_ref"] = F1; pos["S_ref"] = s_open[i + 1]
                if is_last:
                    c = W * EXIT_COST
                    pnl[i] -= c; stats["costs"] += c; stats["expiry_exits"] += 1
                    pos = None
        # ---------- close of bar i: decisions ----------
        if pos is not None:
            if early and not pending_exit:
                k = pos["k"]
                dr = days_to(k, i)
                fc = contracts[k]["c"][i]
                if dr > 0 and not np.isnan(fc):
                    b = (fc / s_close[i] - 1) * 365.0 / dr
                    if b < theta / 4:
                        pending_exit = True
        elif pending_entry is None:
            for k, ct in enumerate(contracts):
                d = days_to(k, i)
                if d >= MIN_DAYS and not np.isnan(ct["c"][i]):
                    b = (ct["c"][i] / s_close[i] - 1) * 365.0 / d
                    if b > theta:
                        pending_entry = k
                    break
    stats["net_pnl_sum"] = float(pnl.sum())
    stats["costs_plus_rebalance"] = stats.pop("costs")
    stats["gross_pnl_sum"] = stats.pop("gross")
    stats["hours_in_position"] = None
    return stats


def main():
    out = {"END": str(END), "W": W, "results": {}}
    for asset in ["BTCUSDT", "ETHUSDT"]:
        idx, so, sc, cts = load_inputs(asset, END)
        out["results"][asset] = {"bars": len(idx), "first_bar": str(idx[0]),
                                 "last_bar": str(idx[-1]),
                                 "contracts": [c["name"] for c in cts]}
        for theta in (0.05, 0.10):
            for early in (False, True):
                name = f"theta{theta:.2f}_{'early' if early else 'expiry'}"
                r = run(idx, so, sc, cts, theta, early)
                r.pop("hours_in_position")
                out["results"][asset][name] = r
                print(asset, name, {k: (round(v, 6) if isinstance(v, float) else v)
                                    for k, v in r.items()})
    (ROOT / "reports" / "h012_independent.json").write_text(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
