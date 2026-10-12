# STATE

## Contador global de pruebas
0

## Qué se está haciendo
Infraestructura (sesión 1). Hecho: src/costs.py, backtest.py (vectorizado, ejecución
en open t+1, funding), metrics.py (Sharpe, MDD, PSR, DSR, bootstrap bloques, PBO-CSCV),
data.py (parser/validador binance.vision, manifest de hashes), checks.py, signals.py.
18 tests OK (`python3 -m pytest -q`): pasos 1–3 del protocolo cubiertos.

## Siguiente paso exacto
Rellenar la cola de HYPOTHESES.md con hipótesis priorizadas (G0 escrito antes de ver
datos). Después: walk-forward con embargo (src/validation.py) y modelo de
margen/liquidación para perps.

## Bloqueos
- Red: data.binance.vision, api.binance.com y fapi.binance.com bloqueados por la
  política de red del entorno (403 en CONNECT). Sin datos no se puede pasar de G0.

## Hipótesis activa
Ninguna.
