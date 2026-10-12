# STATE

## Contador global de pruebas
49  (H001 6 · H002 8 · H003 4 · H004 4 · H005 6 · H006 12 · H007 6 · H008 3)

## Qué se está haciendo
Cerradas (8, todas rechazadas): H001 G4, H002 G5, H003 G2, H004 G2, H005 G3, H006 G3,
H007 G2, H008 G3. En curso: H011 (carry en altcoins con cobertura spot).
Reglas: Sharpe mensual (sharpe_resampled); alfa vs B&H y vs nulo aleatorio; registrar
variantes en HYPOTHESES.md ANTES de ejecutar; tests 1–3 para cada experimento nuevo.

## Siguiente paso exacto
1. Esperar descarga spot 1d (data/spot_daily.log; si se cortó, relanzar
   src.universe.download_spot_daily(um_usdt_symbols())).
2. H011 G2 con las 4 variantes ya fijadas en HYPOTHESES.md (+ tests 1–3 del motor).
3. Anotar en findings/H008 las conclusiones de los subagentes (pasos 4–5).
4. Al cerrar la 10.ª hipótesis: reports/meta_review.md.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H011 (G0, variantes fijadas).
