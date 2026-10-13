# H029 — Diferencial de funding BTC vs ETH (neutral)

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 115).

## Tesis (G0)
Corto en el perp con mayor funding de 7 días y largo en el otro (0,5 por pata) cuando la
diferencia supera d; d ∈ {0,5e-4; 1e-4} (equivalente 8 h); semanal; costes 0,10 %.

## Evidencia (reports/h029.json)
| d | periodo | %/año | Sharpe m. | MDD | semanas activa |
|---|---|---|---|---|---|
| 0,5e-4 | 2020–2022 | −2,8 % | −0,17 | −24,5 % | 40 % |
| 1e-4 | 2020–2022 | −0,4 % | −0,03 | −14,4 % | 26 % |
| 0,5e-4 | 2023–2025 | −1,2 % | −0,34 | −5,8 % | 2 % |
| 1e-4 | 2023–2025 | 0 % | — | 0 % | 0 % |

## Por qué se rechaza
Negativa in-sample: el movimiento relativo ETH/BTC (que tiene tendencias largas, ver
H020) domina al diferencial de funding. Desde 2023 el diferencial casi nunca supera los
umbrales: no hay oportunidad que capturar.

## Reproducibilidad
`python3 experiments/h029_funding_spread.py`.
