# H041 — Reversión del lunes tras el fin de semana

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 138).

## Evidencia (reports/h041.json; BTC y ETH perps diarios)
Apuesta: el lunes (open → close) contra el movimiento del fin de semana.
| condición | periodo | n | media bruta | t | neta (−0,20 %) |
|---|---|---|---|---|---|
| todos | 2020–2022 | 312 | −0,27 % | −0,88 | −0,47 % |
| todos | 2023–2025 | 288 | −0,41 % | −2,00 | −0,61 % |
| |fin de semana| > 5 % | 2020–2022 | 68 | −0,67 % | −0,72 | −0,87 % |
| |fin de semana| > 5 % | 2023–2025 | 28 | −0,97 % | −0,82 | −1,17 % |

## Por qué se rechaza
No hay reversión: el lunes tiende a continuar el movimiento del fin de semana.
Observación (no probada): la continuación del lunes (+0,41 %, t ≈ 2 en 2023–25) apareció
al mirar el OOS; solo podría probarse en el holdout, una vez y contándola.

## Reproducibilidad
`python3 experiments/h041_monday_reversal.py`.
