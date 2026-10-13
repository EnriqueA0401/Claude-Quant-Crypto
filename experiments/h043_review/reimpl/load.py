"""Build daily panels + funding dict from raw zips (uses only src/data.py parsing helpers)."""
import sys, pickle
from pathlib import Path
from multiprocessing import Pool
import pandas as pd

REPO = Path("/home/user/Claude-Quant-Crypto")
sys.path.insert(0, str(REPO))
from src.data import load_klines, load_funding  # parsing helpers only

OUT = Path(__file__).resolve().parent / "panel.pkl"
KL = REPO / "data/futures/um/monthly/klines"


def one(sym):
    try:
        df = load_klines("um", sym, "1d")
    except FileNotFoundError:
        return sym, None, None
    df = df[["open", "high", "low", "close", "quote_volume", "taker_buy_quote"]].copy()
    df.index = df.index.tz_convert(None)
    try:
        f = load_funding(sym)
        f.index = f.index.tz_convert(None)
    except FileNotFoundError:
        f = pd.Series(dtype=float)
    return sym, df, f


if __name__ == "__main__":
    syms = sorted(p.parent.name for p in KL.glob("*/1d"))
    with Pool(4) as p:
        res = p.map(one, syms)
    bars = {s: d for s, d, _ in res if d is not None}
    fund = {s: f for s, _, f in res if f is not None}
    pickle.dump((bars, fund), open(OUT, "wb"))
    print(len(bars), "symbols;", sum(len(f) > 0 for f in fund.values()), "with funding")
