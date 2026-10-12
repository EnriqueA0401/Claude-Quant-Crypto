# STATE

## Contador global de pruebas
0

## Qué se está haciendo
Infraestructura (sesión 1). Hecho: src/costs.py, backtest.py (vectorizado, ejecución
en open t+1, funding), metrics.py (Sharpe, MDD, PSR, DSR, bootstrap bloques, PBO-CSCV),
data.py (parser/validador binance.vision, manifest de hashes), checks.py, signals.py.
18 tests OK (`python3 -m pytest -q`): pasos 1–3 del protocolo cubiertos.

## Siguiente paso exacto
Implementar src/validation.py (splits walk-forward con purga/embargo + holdout final
de 12 meses) con tests. Después: modelo de margen/liquidación para perps. Primera
hipótesis a probar en cuanto haya datos: H001 (G0 ya escrito).

## Bloqueos
- Red: data.binance.vision, api.binance.com y fapi.binance.com bloqueados por la
  política de red del entorno (403 en CONNECT). Sin datos no se puede pasar de G0.

## Hipótesis activa
Ninguna.
