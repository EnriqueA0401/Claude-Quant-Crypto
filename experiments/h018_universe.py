"""Símbolos que alguna vez estuvieron en el top 30 por volumen de 30 días (perps USDT-M).
Uso: python3 experiments/h018_universe.py  → reports/h018_universe.json y descarga metrics."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments"))
import h005_xs_momentum as h5  # noqa: E402
from src.universe import download_metrics  # noqa: E402

o, c, h, qv, fd = h5.panel()
vol30 = qv.rolling(30, min_periods=20).sum()
rank = vol30.rank(axis=1, ascending=False)
ever = sorted(rank.columns[(rank <= 30).any()])
(ROOT / "reports/h018_universe.json").write_text(json.dumps(ever, indent=0) + "\n")
print(len(ever), "símbolos", flush=True)
download_metrics(ever, workers=96)
