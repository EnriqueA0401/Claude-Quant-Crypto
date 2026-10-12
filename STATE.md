# STATE

## Contador global de pruebas
14  (H001: 6 · H002: 8)

## Qué se está haciendo
H001 RECHAZADA en G4 (findings/H001_cash_and_carry.md): 1,4 %/año OOS, 13 entradas.
H002 (momentum series temporales BTC/ETH) en G2: experiments/h002_tsmom.py, 8 variantes.
Regla aprendida: Sharpe siempre con metrics.sharpe_resampled (mensual), nunca horario.

## Siguiente paso exacto
1. Ejecutar experiments/h002_tsmom.py (train 2020–2022) y anotar resultados.
2. Si alguna variante es prometedora: pasos 4–5 del protocolo y G3 walk-forward
   (mismo esquema que experiments/h001_g3_walkforward.py). Si no: rechazar en G2.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
