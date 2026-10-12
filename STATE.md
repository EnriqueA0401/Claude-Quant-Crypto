# STATE

## Contador global de pruebas
14  (H001: 6 · H002: 8)

## Qué se está haciendo
Cerradas: H001 rechazada (G4), H002 rechazada (G5). Ver findings/.
Activa: H003 (funding extremo → retorno negativo del perp), solo G0 escrito.
Reglas aprendidas: Sharpe con metrics.sharpe_resampled; medir alfa frente a buy & hold.

## Siguiente paso exacto
H003 · G2: fijar variantes en HYPOTHESES.md ANTES de ejecutar (umbral = percentil
del funding calculado solo con datos pasados; horizonte de tenencia 24/72 h), escribir
experiments/h003_funding_extreme.py y correr train 2020–2022 en BTC/ETH.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
