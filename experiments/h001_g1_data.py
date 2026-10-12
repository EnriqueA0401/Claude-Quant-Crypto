"""H001 · G1: calidad de datos de klines 1h (spot y perp) y funding."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data import load_funding, load_klines, validate_bars  # noqa: E402
from src.download import SYMBOLS  # noqa: E402

out = {}
for sym in SYMBOLS:
    for mkt in ["spot", "um"]:
        df = load_klines(mkt, sym)
        rep = validate_bars(df, "1h")
        rep["start"], rep["end"] = str(df.index.min()), str(df.index.max())
        out[f"{mkt}:{sym}"] = rep
    f = load_funding(sym)
    gaps = f.index.to_series().diff().dt.total_seconds().div(3600)
    out[f"funding:{sym}"] = {"rows": len(f), "start": str(f.index.min()),
                             "end": str(f.index.max()),
                             "interval_hours_counts": gaps.round(2).value_counts().head(6).to_dict(),
                             "min_rate": float(f.min()), "max_rate": float(f.max())}
dest = Path(__file__).resolve().parents[1] / "reports/h001_g1_data.json"
dest.write_text(json.dumps(out, indent=1, default=str) + "\n")
for k, v in out.items():
    print(k, {x: v[x] for x in v if x in ("rows", "duplicates", "missing_bars", "bad_ohlc",
                                          "non_positive", "interval_hours_counts")})
