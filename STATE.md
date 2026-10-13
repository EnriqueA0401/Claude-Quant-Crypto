# STATE

## Contador global de pruebas
87  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (21, todas rechazadas; H014 por cota superior). Meta-review 2 escrita (reports/meta_review.md):
agotadas las familias direccionales cross-sectional de altcoins, eventos de crowding
y arbitrajes taker. Única señal limpia: carry trimestral BTC/ETH (< efectivo).
Reglas: comparar con caja (≈ 4–5 %/año); Sharpe mensual; alfa vs B&H y nulo aleatorio;
variantes registradas antes de ejecutar; tests 1–3; liquidaciones pesimistas;
desempates deterministas; validar vencimientos y barras sin operaciones (G1).

## Siguiente paso exacto
1. Prioridad 2 de la meta-review 2: cartera carry BTC/ETH (H012 trimestral + H001 perp
   cuando H012 no está invertido) contra el rendimiento de USDT. Fijar diseño en
   HYPOTHESES.md (H021) antes de ejecutar; juzgar 2023-01 → 2025-09.
2. Si falla: cerrar la familia carry y documentar en STATE que con < 1.000 USD, VIP0 y
   costes taker no se ha encontrado ventaja tras 21 hipótesis; proponer nuevas fuentes
   (datos externos: on-chain, opciones Deribit, order book) para la siguiente fase.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
