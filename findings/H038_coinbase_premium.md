# H038 — Prima de Coinbase como señal de demanda de EE. UU.

**Veredicto: RECHAZADA en G2/G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 132).

## Tesis (G0)
Largo en el perp BTCUSDT solo cuando la prima de Coinbase (BTC-USD / BTCUSDT − 1) supera
su media de W días; W ∈ {7, 30}; costes 0,10 % por lado; funding.

## Evidencia (reports/h038.json)
| W | periodo | %/año | Sharpe m. | MDD | B&H: %/año, Sharpe | alfa (beta) |
|---|---|---|---|---|---|---|
| 30 (elegida) | 2020–2022 | 29,0 % | 0,54 | −53 % | 38,9 %, 0,55 | +11,8 % (0,44), n.s. |
| 7 | 2020–2022 | 19,0 % | 0,35 | −60 % | 38,9 %, 0,55 | −0,9 % (0,51) |
| 30 (elegida) | 2023–2025 | 49,6 % | 1,08 | −41 % | 72,7 %, 1,57 | +11,6 % (0,52), n.s. |
| 7 | 2023–2025 | 32,5 % | 0,80 | −39 % | 72,7 %, 1,57 | −4,5 % (0,51) |

## Por qué se rechaza
No mejora el Sharpe de buy & hold ni in-sample (0,54 frente a 0,55) ni OOS (1,08 frente
a 1,57); el alfa no es significativo. La prima mezcla demanda real con el diferencial
USD/USDT.

## Reproducibilidad
`python3 experiments/h038_coinbase_premium.py` (velas de Coinbase con hash).
