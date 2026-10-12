# STATE

## Contador global de pruebas
49  (H001 6 · H002 8 · H003 4 · H004 4 · H005 6 · H006 12 · H007 6 · H008 3)

## Qué se está haciendo
Cerradas (7, todas rechazadas): H001 G4, H002 G5, H003 G2, H004 G2, H005 G3, H006 G3,
H007 G2. En curso: H008 (carry cross-sectional de funding), G2 ejecutándose.
Reglas: Sharpe mensual (sharpe_resampled); alfa vs B&H y vs nulo aleatorio; registrar
variantes en HYPOTHESES.md ANTES de ejecutar; tests 1–3 para cada experimento nuevo.

## Siguiente paso exacto
1. Leer reports/h008_g2.json (o relanzar experiments/h008_funding_xs.py) y decidir G3.
2. Siguientes en cola: H011 (carry en altcoins), H009 (basis), H010 (volumen).
   Fijar variantes en HYPOTHESES.md antes de ejecutar. Meta-review al cerrar la 10.ª.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H008 (G2).
