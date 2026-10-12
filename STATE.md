# STATE

## Contador global de pruebas
53  (H001 6 · H002 8 · H003 4 · H004 4 · H005 6 · H006 12 · H007 6 · H008 3 · H011 4)

## Qué se está haciendo
Cerradas (9, todas rechazadas): H001 G4, H002 G5, H003 G2, H004 G2, H005 G3, H006 G3,
H007 G2, H008 G3, H011 G3. Pendientes: H009 (basis), H010 (volumen).
Motor semanal (experiments/h005_xs_momentum) corregido tras pasos 4–5: desempate
determinista, funding equivalente a 8 h, barras con volumen 0 no operables.
Reglas: Sharpe mensual; alfa vs B&H y nulo aleatorio; variantes registradas antes de
ejecutar; tests 1–3 por experimento; liquidaciones pesimistas.

## Siguiente paso exacto
1. H010 (prima de alto volumen, datos 1d ya descargados): fijar variantes en
   HYPOTHESES.md, escribir experimento + tests 1–3 y ejecutar G2.
2. Al cerrarla (10.ª hipótesis): reports/meta_review.md (familias agotadas, patrón
   "2020–2022 in-sample engaña", ¿cambiar de enfoque?).
3. Después H009 (basis spot-perp 1h, 5 pares ya descargados).

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna (siguiente: H010).
