"""H001 independent event-driven reimplementation (code-review protocol step 4).

Cash-and-carry: long spot + short USDT-M perp, equal notional w = 0.5 of capital.
Written from the spec only, without reading src/ or experiments/h001_carry.py.

Run:  python experiments/h001_independent.py
Out:  reports/h001_independent.json
"""
import csv
import glob
import io
import json
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "reports", "h001_independent.json")

HOUR_MS = 3_600_000
END_MS = 1672531200000  # 2023-01-01 00:00 UTC
W = 0.5
ENTRY_COST = 0.0015 + 0.0010  # spot fee+slip, perp fee+slip (per unit notional change)
REB_COST = 0.25 * 0.0025
REB_THRESH = 0.25
LIQ_MULT = 2 - 0.005

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
THETAS = [0.0001, 0.0002, 0.0003]
KS = [1, 3]


def norm_ts(v):
    """Return ms since epoch; values > 1e14 are microseconds."""
    v = int(v)
    return v // 1000 if v > 10**14 else v


def read_zip_rows(path):
    with zipfile.ZipFile(path) as z:
        name = z.namelist()[0]
        with z.open(name) as fh:
            for row in csv.reader(io.TextIOWrapper(fh, "utf-8")):
                if not row:
                    continue
                try:
                    int(float(row[0]))
                except ValueError:
                    continue  # header row
                yield row


def load_klines(pattern):
    """dict open_time_ms -> (open, high); first occurrence kept (files sorted)."""
    bars = {}
    for f in sorted(glob.glob(pattern)):
        for row in read_zip_rows(f):
            t = norm_ts(row[0])
            if t not in bars:
                bars[t] = (float(row[1]), float(row[2]))
    return bars


def load_perp(sym):
    bars = load_klines(os.path.join(DATA, "futures/um/monthly/klines", sym, "1h", "*.zip"))
    daily = load_klines(os.path.join(DATA, "futures/um/daily/klines", sym, "1h", "*.zip"))
    for t, v in daily.items():
        if t not in bars:  # monthly wins
            bars[t] = v
    return bars


def load_funding(sym):
    ev = {}
    for f in sorted(glob.glob(os.path.join(DATA, "futures/um/monthly/fundingRate", sym, "*.zip"))):
        for row in read_zip_rows(f):
            t = norm_ts(row[0])
            t = ((t + 30_000) // 60_000) * 60_000  # round to nearest minute
            if t < END_MS and t not in ev:
                ev[t] = float(row[2])
    return sorted(ev.items())


def funding_states(events, theta, k):
    """State after each event (hysteresis)."""
    states = []
    state = 0
    window = []
    for _, r in events:
        window.append(r)
        if len(window) > k:
            window.pop(0)
        if len(window) == k:
            m = sum(window) / k
            if m > theta:
                state = 1
            elif m < theta / 2:
                state = 0
        states.append(state)
    return states


def run(sym, theta, k, perp, spot, mark, events):
    times = sorted(t for t in perp if t < END_MS)
    start = next(i for i, t in enumerate(times) if t in spot)
    times = times[start:]
    n = len(times)

    # aligned spot with carry-forward and tradable flag
    spot_open, tradable = [], []
    last = None
    for t in times:
        if t in spot:
            last = spot[t][0]
            spot_open.append(last)
            tradable.append(True)
        else:
            spot_open.append(last)
            tradable.append(False)

    states = funding_states(events, theta, k)
    ev_i = 0          # pointer for signal (events with time <= close of bar)
    fund_i = 0        # pointer for funding accrual
    # skip events at or before the first bar open for accrual
    while fund_i < len(events) and events[fund_i][0] <= times[0]:
        fund_i += 1

    pos = 0           # broker position (0/1) currently held
    desired = 0       # decision from previous bar
    ref = None
    acc = dict(n_bars=0, sum_net=0.0, sum_funding=0.0, sum_basis=0.0, sum_cost=0.0,
               sum_rebalance=0.0, entries=0, liquidations=0)

    for t in range(n - 1):
        o_t, o_n = times[t], times[t + 1]
        # 1. position change at open of bar t
        new_pos = desired if (t > 0 and tradable[t]) else pos
        if t == 0:
            new_pos = 0
        cost = abs(new_pos - pos) * W * ENTRY_COST
        if new_pos == 1 and pos == 0:
            acc["entries"] += 1
            ref = perp[o_t][0]
        if new_pos == 0:
            ref = None
        pos = new_pos

        # funding events in (open[t], open[t+1]]
        fsum = 0.0
        while fund_i < len(events) and events[fund_i][0] <= o_n:
            if events[fund_i][0] > o_t:
                fsum += events[fund_i][1]
            fund_i += 1

        basis = funding = reb = liq = 0.0
        if pos == 1:
            hm = mark[o_t][1] if o_t in mark else perp[o_t][1]
            if hm >= ref * LIQ_MULT:
                liq = -W
                acc["liquidations"] += 1
                pos = 0
                ref = None
            else:
                basis = W * (spot_open[t + 1] / spot_open[t] - perp[o_n][0] / perp[o_t][0])
                funding = W * fsum
                if abs(perp[o_n][0] / ref - 1) > REB_THRESH:
                    reb = W * REB_COST
                    ref = perp[o_n][0]
        net = basis + funding - cost - reb + liq

        acc["n_bars"] += 1
        acc["sum_net"] += net
        acc["sum_funding"] += funding
        acc["sum_basis"] += basis
        acc["sum_cost"] += cost
        acc["sum_rebalance"] += reb

        # 2. decision at close of bar t -> position for bar t+1
        close = o_t + HOUR_MS
        while ev_i < len(events) and events[ev_i][0] <= close:
            ev_i += 1
        desired = states[ev_i - 1] if ev_i > 0 else 0

    acc["first_bar"] = times[0]
    acc["last_bar_used"] = times[n - 2]
    acc["n_untradable_bars"] = sum(1 for x in tradable if not x)
    return acc


def main():
    out = {}
    for sym in SYMBOLS:
        perp = load_perp(sym)
        spot = load_klines(os.path.join(DATA, "spot/monthly/klines", sym, "1h", "*.zip"))
        mark = load_klines(os.path.join(DATA, "futures/um/monthly/markPriceKlines", sym, "1h", "*.zip"))
        events = load_funding(sym)
        for theta in THETAS:
            for k in KS:
                key = f"{sym}|theta={theta}|k={k}"
                out[key] = run(sym, theta, k, perp, spot, mark, events)
                r = out[key]
                print(f"{key:32s} net={r['sum_net']:.4f} fund={r['sum_funding']:.4f} "
                      f"basis={r['sum_basis']:.4f} cost={r['sum_cost']:.4f} "
                      f"reb={r['sum_rebalance']:.4f} entries={r['entries']} liq={r['liquidations']}")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=1)


if __name__ == "__main__":
    main()
