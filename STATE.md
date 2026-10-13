# STATE

## Contador global de pruebas
83  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (20, todas rechazadas). Meta-review 2 escrita (reports/meta_review.md):
agotadas las familias direccionales cross-sectional de altcoins, eventos de crowding
y arbitrajes taker. Única señal limpia: carry trimestral BTC/ETH (< efectivo).
Reglas: comparar con caja (≈ 4–5 %/año); Sharpe mensual; alfa vs B&H y nulo aleatorio;
variantes registradas antes de ejecutar; tests 1–3; liquidaciones pesimistas;
desempates deterministas; validar vencimientos y barras sin operaciones (G1).

## Siguiente paso exacto
1. H014 (ejecución maker): descargar aggTrades de BTCUSDT y ETHUSDT perp + spot de
   1 mes (2022-06, train) y construir src/fills.py: fill de una orden limit solo si un
   trade posterior cruza el precio (estrictamente) dentro de T minutos; si no, taker.
   Tests con trades sintéticos. Después re-evaluar H009 (basis 1h) con costes maker.
2. Prioridad 2 de la meta-review: cartera carry BTC/ETH (H012 + H001) contra USDT.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
