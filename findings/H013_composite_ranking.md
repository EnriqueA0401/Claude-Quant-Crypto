# H013 — Ranking semanal compuesto de señales débiles (walk-forward)

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 61).

## Tesis (G0)
Momentum (1 y 4 semanas), funding de 7 días, ratio de volumen y volatilidad no pagan
costes por separado; combinadas en un ranking, podrían. Modelos: ridge (λ = 1) sobre
percentiles cross-sectional y suma con el signo de la IC. Reentreno cada 6 meses con
todo el pasado y 1 semana de embargo. Motor de H005 (5+5, costes 0,15 %, funding).

## Evidencia
- G2 (folds 2021–2022 dentro del train; reports/h013_g2.json): ridge 56 %/año, Sharpe
  1,36, MDD −38 %, IC95 semanal [−0,25 %, +2,66 %]. Signo de IC: 29 %/año, Sharpe 0,68.
- G3 (folds 2023-01 → 2025-09; reports/h013_g3.json):
  **ridge 17,7 %/año, Sharpe 0,43, MDD −43 %, IC95 [−0,45 %, +1,19 %];**
  2023 −13 %, 2024 +4 %, 2025 +58 %. Signo de IC: −53 %/año (IC95 < 0).

## Por qué se rechaza
IC95 incluye 0, negativa o plana en 2 de 3 años y MDD del 43 %. La versión por signo
de IC pierde con claridad: las relaciones aprendidas en 2020–2022 se invierten después.

## Qué se aprendió
- Combinar señales que individualmente dependen del régimen 2020–2021 no las vuelve
  robustas: el modelo aprende ese régimen.
- Cuarta confirmación del patrón de la meta-review: cualquier señal direccional
  cross-sectional semanal en altcoins se desvanece en 2023–2025.

## Reproducibilidad
`python3 experiments/h013_composite.py` (G2) y `... g3` (G3). Test en tests/test_h005_h006.py.
