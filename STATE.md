# STATE

## Contador global de pruebas
55  (H001 6 · H002 8 · H003 4 · H004 4 · H005 6 · H006 12 · H007 6 · H008 3 · H010 2 · H011 4)

## Qué se está haciendo
Cerradas (10, todas rechazadas). Meta-review 1 escrita (reports/meta_review.md): cambio
de enfoque hacia carry fijado (H012), combinación de señales (H013) y ejecución maker
(H014). Motor semanal corregido tras pasos 4–5.
Reglas: Sharpe mensual; alfa vs B&H y nulo aleatorio; variantes registradas antes de
ejecutar; tests 1–3 por experimento; liquidaciones pesimistas.

## Siguiente paso exacto
H012: descargar klines 1h de futuros trimestrales BTC/ETH (futures/um, símbolos
BTCUSDT_YYMMDD) + spot 1h ya disponible; fijar variantes en HYPOTHESES.md antes de
ejecutar; motor con tests 1–3; G2 en vencimientos 2021–2022.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H012 (G0 escrito).
