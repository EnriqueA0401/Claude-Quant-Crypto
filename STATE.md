# STATE

## Contador global de pruebas
0

## Qué se está haciendo
Infraestructura (sesión 1). Hecho: src/costs.py, backtest.py (vectorizado, ejecución
en open t+1, funding), metrics.py (Sharpe, MDD, PSR, DSR, bootstrap bloques, PBO-CSCV),
data.py (parser/validador binance.vision, manifest de hashes), checks.py, signals.py.
validation.py (holdout 12 meses, walk-forward con purga/embargo).
22 tests OK (`python3 -m pytest -q`): pasos 1–3 del protocolo cubiertos.
Cola H001–H007 con G0 escrito en HYPOTHESES.md.

## Siguiente paso exacto
1. Comprobar acceso a data.binance.vision (curl a un zip de klines).
2. Si hay acceso: descargar BTCUSDT/ETHUSDT spot+perp klines 1h y funding desde 2020,
   pasar G1 (validate_bars) y empezar H001.
3. Si no: implementar src/margin.py (margen aislado, precio de liquidación USDT-M) con tests.

## Bloqueos
- Red: data.binance.vision, api.binance.com y fapi.binance.com bloqueados por la
  política de red del entorno (403 en CONNECT). Sin datos no se puede pasar de G0.

## Hipótesis activa
Ninguna.
