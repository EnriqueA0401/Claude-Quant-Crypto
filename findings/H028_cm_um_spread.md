# H028 — Convergencia COIN-M vs USDT-M del mismo trimestral

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 113).

## Tesis (G0)
Mercados segmentados (COIN-M y USDT-M) separan el precio de contratos que liquidan al
mismo índice; la posición contraria hasta el vencimiento captura la convergencia.
s ∈ {5 %, 10 %} anualizado, ambas direcciones, BTC y ETH, motor de H012, 4 lados de
costes de futuros (0,10 % por lado).

## Evidencia (reports/h028.json)
| s | periodo | %/año | Sharpe m. | MDD | entradas (total) |
|---|---|---|---|---|---|
| 5 % | 2021–2022 | +2,99 % | 1,43 | −0,6 % | 95 |
| 5 % | **2023–2025** | **−0,09 %** | −1,16 | −0,2 % | |
| 10 % | 2021–2022 | +2,83 % | 1,23 | −0,5 % | 37 |
| 10 % | **2023–2025** | **+0,03 %** | 0,60 | −0,1 % | |

## Por qué se rechaza
La ineficiencia existía en 2021–2022 y desapareció en 2023–2025 (retorno OOS ≈ 0): el
arbitraje entre COIN-M y USDT-M quedó cerrado por otros participantes.

## Qué se aprendió
Las ineficiencias de estructura de mercado en BTC/ETH en Binance se cierran con el
tiempo; lo que funcionó en 2021 no es una ventaja actual.

## Reproducibilidad
`python3 experiments/h028_cm_um_spread.py`.
