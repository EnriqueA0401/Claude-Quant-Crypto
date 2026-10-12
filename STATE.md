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
Descargar BTCUSDT/ETHUSDT spot + perp USDT-M klines 1h y fundingRate desde 2020 de
data.binance.vision (src/data.fetch), pasar G1 (validate_bars) y empezar H001.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
