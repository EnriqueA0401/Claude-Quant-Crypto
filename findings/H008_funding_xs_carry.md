# H008 — Carry cross-sectional de funding (largo funding bajo, corto funding alto)

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-12. Variantes: 3 (contador global: 49).

## Tesis (G0)
Los pares con funding alto están llenos de largos apalancados que pagan por estar ahí;
un long/short semanal (5 + 5, top 50 por volumen, deslistados incluidos) cobra ese
funding. Orden por funding medio de los D días previos, D ∈ {3, 7, 14}.

## Evidencia
- G2 (2020-04 → 2022-12, 140 semanas; reports/h008_g2.json): D = 3/7 → 76–80 %/año,
  Sharpe mensual 1,9, MDD 23–30 %, **IC95 semanal > 0**. Funding ≈ 24 %/año del total;
  el resto venía del precio (los pares con funding alto cayeron).
- G3 walk-forward, folds de 6 meses desde 2023 (reports/h008_g3.json):
  **OOS −9,9 %/año, Sharpe −0,25, MDD −58 %, IC95 [−1,0 %, +0,76 %] semanal.**
  Descomposición OOS: funding +33 %/año, precio −33 %/año, costes −10 %/año.
  Costes ×2: −20 %/año. Por año: 2023 +0,5 %, 2024 −12,8 %, 2025 −14,7 %.

## Por qué se rechaza
Negativa fuera de muestra y en 2 de 3 años. El componente de precio que daba la ventaja
in-sample (2020–2022) se invirtió: en 2023–2025 los pares con funding alto siguieron
subiendo (momentum) más de lo que pagaban.

## Qué se aprendió
- El funding se cobra de verdad y es grande en altcoins (~33 %/año sobre 0,5 de capital
  por lado), pero la exposición direccional lo anula. Motiva H011 (mismo funding con
  cobertura spot).
- Segundo caso (tras H005) en que 2020–2022 da un in-sample excelente que no se repite:
  ese periodo de train es poco representativo. Considerar en la meta-review.
- Pasos 4–5 del protocolo lanzados en paralelo; sus conclusiones se anotan abajo.

## Reproducibilidad
`python3 experiments/h008_funding_xs.py && python3 experiments/h008_g3_walkforward.py`.
