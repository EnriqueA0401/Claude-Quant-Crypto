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
- Pasos 4–5 del protocolo (ver abajo) cambiaron cifras pero no el veredicto.

## Reproducibilidad
`python3 experiments/h008_funding_xs.py && python3 experiments/h008_g3_walkforward.py`.

## Protocolo (pasos 4 y 5) y re-ejecución
- Paso 4: la reimplementación independiente (experiments/h008_independent.py) difería en
  12–49 semanas. Causa explicada al 100 %: empates en el funding por defecto (0,01 %) y
  ruido de coma flotante; el desempate dependía de un argsort inestable. Corregido con
  redondeo a 1e-10 y desempate por nombre (experiments/h005_xs_momentum._rank).
- Paso 5 (revisor): sin lookahead ni errores de signo. Corregido: funding equivalente a
  8 h (65 % de pares-día con funding no-8 h en 2025), barras con volumen 0 no operables,
  días de klines faltantes rellenados con ficheros diarios.
- Re-ejecución con todo corregido: G2 D=3/7 → 73–83 %/año, Sharpe 1,8–2,0, IC95 > 0.
  **G3 OOS: +15,6 %/año, Sharpe 0,33, MDD −44 %, IC95 semanal [−0,79 %, +1,43 %].**
  Funding +34 %/año, precio −9 %/año. 2023 −1,7 %, 2024 +35,7 %, 2025 +8,9 %.
  Sigue rechazada: IC95 incluye 0, Sharpe 0,33 y MDD 44 % no tolerable con 1.000 USD.
