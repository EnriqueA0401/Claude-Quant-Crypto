# H006 — Deriva negativa tras el listado de perps USDT-M

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-12. Variantes: 12 (contador global tras H005/H006: 42).

## Tesis (G0)
Los compradores minoristas atraídos por el hype del listado pagan de más; un corto 1x
en los primeros días gana neto de costes (0,05 % + 0,15 % slippage por lado) y funding.
Universo completo de 900 perps USDT-M, incluidos los deslistados (sin sesgo de supervivencia).

## Evidencia
- G2 (listados 2020–2022, 163 eventos, 32 meses; reports/h006_g2.json): media +2–7 % por
  evento y mediana +8–20 % en las 12 variantes, pero IC95 por meses incluye 0 en todas.
  Sin stop, 3–22 liquidaciones (high ≥ 2× entrada) se comen la media; con stop al +30 %
  desaparecen. Las 6 variantes con stop se registraron antes de ver su resultado.
- G3 walk-forward por fecha de listado, folds de 6 meses desde 2023, purga de 31 días,
  holdout excluido (reports/h006_g3.json): casi siempre se elige E=2, N=7, stop 30 %.
  **OOS: 408 eventos, media +0,5 %, mediana +4,0 %, t = 0,25, IC95 [−3,5 %, +4,5 %].**
  Por año: 2023 −1,6 % (99), 2024 +3,2 % (131), 2025 −0,3 % (178). Último fold −12 %.

## Por qué se rechaza
La media OOS no se distingue de 0 (t = 0,25) y es negativa en 2 de 3 años. La mediana
positiva no sirve: la cola derecha de pumps la compensa.

## Qué se aprendió
- El efecto "nuevos listados caen" existe en mediana, pero los pumps en la cola hacen que
  un corto no tenga esperanza positiva tras costes. Un stop limita la cola pero dispara a
  menudo y se lleva el beneficio.
- Con datos diarios el stop es aproximado (fill en max(nivel, open)); con datos 1h podría
  ser algo peor por mechas intradía, lo que refuerza el rechazo.

## Reproducibilidad
`python3 -m src.universe && python3 experiments/h006_listing.py &&
python3 experiments/h006_g3_walkforward.py`. Tests: tests/test_h005_h006.py.
