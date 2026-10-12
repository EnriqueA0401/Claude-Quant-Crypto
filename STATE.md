# STATE

## Contador global de pruebas
42  (H001: 6 · H002: 8 · H003: 4 · H007: 6 · H006: 12 · H005: 6)

## Qué se está haciendo
Cerradas (6, todas rechazadas): H001 G4, H002 G5, H003 G2, H005 G3, H006 G3, H007 G2.
Pendiente: H004 (reversión tras liquidaciones). Universo USDT-M completo descargado.
Reglas: Sharpe mensual (sharpe_resampled); alfa vs B&H y vs nulo aleatorio; registrar
variantes en HYPOTHESES.md ANTES de ejecutar; tests 1–3 para cada experimento nuevo.

## Siguiente paso exacto
1. H004: descargar futures/um/daily/metrics (open interest 5 min) de BTC/ETH y fijar
   variantes en HYPOTHESES.md antes de ejecutar G2.
2. Añadir a la cola 4+ hipótesis nuevas (p. ej. basis spot-perp extremo, volumen
   anómalo, carry en altcoins con funding persistente, órdenes maker). Al cerrar la
   10.ª hipótesis: reports/meta_review.md.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H004 (variantes fijadas; descargando metrics de OI).
