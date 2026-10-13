# H036 — Emisión neta de stablecoins como señal de timing

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 128).

## Tesis (G0)
La emisión neta de stablecoins USD indica entrada de liquidez; estar largo (perp 1x) en
BTC/ETH solo si la oferta creció en D días (7 o 30). Datos DefiLlama (con hash).

## Evidencia (reports/h036.json)
| D | periodo | %/año | Sharpe m. | MDD | B&H: %/año, Sharpe | alfa (beta) |
|---|---|---|---|---|---|---|
| 7 (elegida) | 2020–2022 | 72,2 % | 1,14 | −64 % | 70,8 %, 0,94 | +13,9 % (0,82), n.s. |
| 30 | 2020–2022 | 70,8 % | 1,12 | −57 % | 70,8 %, 0,94 | +15,0 % (0,79), n.s. |
| 7 (elegida) | **2023–2025** | **32,9 %** | **0,69** | **−54 %** | **64,5 %, 1,26** | **−12,3 % (0,70)** |
| 30 | 2023–2025 | 46,2 % | 0,99 | −49 % | 64,5 %, 1,26 | −5,6 % (0,80) |

## Por qué se rechaza
Mejora no significativa in-sample y claramente peor que buy & hold OOS (alfa −12 %/año).
Séptimo caso del patrón "2020–2022 engaña"; confirma lo agotado de la familia de timing.

## Reproducibilidad
`python3 experiments/h036_stablecoin_supply.py`.
