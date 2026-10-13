# H021 — Cartera carry "cash-plus" BTC/ETH (trimestral + perp)

**Veredicto: RECHAZADA (no supera el rendimiento de USDT).** Fecha: 2026-10-13. Variantes: 1 (contador global: 88).

## Evidencia (reports/h021.json, OOS 2023-01 → 2025-09)
**3,5 %/año sobre capital, Sharpe 1,66, MDD −1,1 %, IC95 > 0**; 2023 +1,7 %, 2024 +6,1 %,
2025 +1,9 %. El trimestral está invertido el 88–94 % del tiempo; el perp casi nunca
(≈ 1 % del tiempo) y no aporta (≈ 0 %/año).

## Por qué se rechaza
El listón fijado era > 5 %/año (rendimiento de USDT): 3,5 % no lo supera.

## Qué se aprendió
El carry trimestral de BTC/ETH es casi permanente en 2023–2025 (basis > 5 % anual la
mayor parte del tiempo) y su retorno sobre capital está limitado por la estructura:
la mitad del capital queda parada como margen USDT del corto. Motiva H022 (estructura
COIN-M: la moneda comprada es a la vez el margen del corto).
