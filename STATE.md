# STATE

## Contador global de pruebas
18  (H001: 6 · H002: 8 · H003: 4)

## Qué se está haciendo
Cerradas (3): H001 rechazada G4, H002 rechazada G5, H003 rechazada G2. Ver findings/.
Reglas aprendidas: Sharpe con metrics.sharpe_resampled; medir alfa frente a buy & hold
y frente a un nulo de entradas aleatorias; rangos de percentil estrictos (empates).

## Siguiente paso exacto
Elegir la siguiente hipótesis. Candidatas por coste/prior:
- H007 (estacionalidad intradía): datos ya descargados, coste bajo, prior bajo.
- H005 / H006: requieren universo de perps con deslistados (descargar lista de
  símbolos de data.binance.vision, incluidos los deslistados).
Plan: fijar variantes de H007 en HYPOTHESES.md y ejecutar G2; en paralelo, descargar
el universo completo de perps USDT-M (klines 1d + funding) para H005/H006.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna (siguiente: H007).
