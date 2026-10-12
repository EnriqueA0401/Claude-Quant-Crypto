# STATE

## Contador global de pruebas
0

## Qué se está haciendo
H001 (cash-and-carry). Datos descargados (5 pares, 2020-01→2026-09, 1h + funding) y
G1 superado: reports/h001_g1_summary.md. Librería base y 23 tests OK.

## Siguiente paso exacto
H001 · G2: experiments/h001_carry.py. Diseño fijado antes de ver resultados:
- Largo spot + corto perp, apalancamiento 1x (N = capital/2), costes 4 lados.
- Entrada si media de las últimas k liquidaciones de funding > θ; salida si < θ/2.
- Variantes: θ ∈ {0.0001, 0.0002, 0.0003}, k ∈ {1, 3} → 6 (sumar al contador).
- Train G2: 2020-01→2022-12 solo BTC/ETH. Holdout: 2025-10→2026-09 (no tocar).
- Rebalanceo con coste de ida y vuelta si el perp se mueve ±25% desde la entrada.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
