# H005 — Momentum / reversión cross-sectional semanal en perps USDT-M

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-12. Variantes: 6 (contador global: 42).

## Tesis (G0)
Infrarreacción y herding entre activos: los ganadores de las últimas L semanas siguen
ganando. Universo semanal: top 50 por volumen de 30 días con ≥ 90 días de historia,
incluidos deslistados. 5 largos + 5 cortos, 0,5 de capital por lado, costes 0,15 % por
lado, funding real, cortos liquidados si el high semanal ≥ 2× entrada.

## Evidencia
- G2 (2020-04 → 2022-12, 140 semanas; reports/h005_g2.json): momentum 30–42 %/año,
  Sharpe mensual 0,66–0,94, MDD 47–64 %; la reversión pierde en espejo (−67 %/año).
  IC95 semanal incluye 0 en las tres variantes de momentum.
- G3 walk-forward, folds de 6 meses desde 2023 (reports/h005_g3.json): se elige L = 4
  (y L = 1 en el último fold). **OOS: 23 %/año, Sharpe 0,36, MDD −57 %, IC95 semanal
  [−0,77 %, +1,80 %].** Por año: 2023 −3,9 %, 2024 −4,3 %, 2025 +71,5 %.

## Por qué se rechaza
El IC95 incluye 0 y todo el beneficio OOS viene de 2025: pierde en 2 de 3 años, con un
drawdown del 57 % que no es tolerable con 1.000 USD.

## Qué se aprendió
- En 2020–2022 el momentum cross-sectional funcionó in-sample, pero en 2023–2024 no.
  El efecto depende del régimen (o del periodo de euforia de altcoins).
- La reversión semanal es claramente perdedora: confirma que el ranking tiene algo de
  persistencia, pero no lo bastante estable para pagar 0,15 % por lado y el riesgo de cola.

## Reproducibilidad
`python3 experiments/h005_xs_momentum.py && python3 experiments/h005_g3_walkforward.py`.
