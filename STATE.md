# STATE

## Contador global de pruebas
73  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (17, todas rechazadas): H001–H013, H015–H017. La mejor: H012 (basis
trimestral BTC/ETH, OOS 3,3 %/año tras corrección) no supera al efectivo ni generaliza.
Patrón dominante: señales cross-sectional "significativas" en 2020–2022 se invierten en
2023–2025 (H002, H005, H008, H013, H016).
Pendientes: H014 (maker), H017 (tendencia multi-moneda), H018 (purga de OI diaria).

## Siguiente paso exacto
1. H018 (variantes fijadas, experiments/h018_oi_flush.py + test listos): esperar a que
   termine la descarga de metrics de 380 símbolos (data/h018_metrics.log; si se cortó,
   relanzar python3 experiments/h018_universe.py: retoma lo descargado) y ejecutar.
3. Meta-review 2 al cerrar la 20.ª hipótesis.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna (siguiente: nuevas hipótesis + H014).
