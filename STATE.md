# STATE

## Contador global de pruebas
24  (H001: 6 · H002: 8 · H003: 4 · H007: 6)

## Qué se está haciendo
Cerradas (4): H001 rech. G4, H002 rech. G5, H003 rech. G2, H007 rech. G2. Ver findings/.
Descargando universo USDT-M completo (900 símbolos, klines 1d + funding): data/universe.log.
Reglas aprendidas: Sharpe con metrics.sharpe_resampled; medir alfa frente a buy & hold
y frente a un nulo de entradas aleatorias; rangos de percentil estrictos (empates).

## Siguiente paso exacto
1. Cuando termine `python3 -m src.universe` (si se cortó, relanzarlo: retoma lo ya
   descargado), pasar G1 al universo (huecos, primeras/últimas fechas = listado/delist).
2. H006 (deriva tras listado de perps): fijar variantes en HYPOTHESES.md y ejecutar G2.
3. Después H005 (momentum cross-sectional) con el mismo universo.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna (siguiente: H007).
