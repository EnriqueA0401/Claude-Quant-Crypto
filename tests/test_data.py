import pandas as pd

from src.data import parse_klines, validate_bars

ROW = "{t},100,101,99,100.5,10,{c},1000,5,4,400,0\n"


def _csv(times, header=False):
    s = ",".join(["open_time", "open", "high", "low", "close", "volume", "close_time",
                  "quote_volume", "count", "tbb", "tbq", "ignore"]) + "\n" if header else ""
    return "".join([s] + [ROW.format(t=t, c=t + 59_999) for t in times]).encode()


def test_parse_ms_and_us_timestamps():
    ms = 1_704_067_200_000          # 2024-01-01 00:00 UTC
    us = 1_735_689_600_000_000      # 2025-01-01 00:00 UTC (formato spot 2025+)
    df = parse_klines(_csv([ms, us]))
    assert list(df.index) == [pd.Timestamp("2024-01-01", tz="UTC"),
                              pd.Timestamp("2025-01-01", tz="UTC")]


def test_parse_with_header():
    df = parse_klines(_csv([1_704_067_200_000], header=True))
    assert len(df) == 1 and df["close"].iloc[0] == 100.5


def test_validate_detects_gaps_and_duplicates():
    t0 = 1_704_067_200_000
    m = 60_000
    df = parse_klines(_csv([t0, t0 + m, t0 + m, t0 + 3 * m]))
    rep = validate_bars(df, "1min")
    assert rep["duplicates"] == 1
    assert rep["missing_bars"] == 1
    assert rep["bad_ohlc"] == 0
