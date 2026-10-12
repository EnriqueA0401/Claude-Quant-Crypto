# H015 — Efecto MAX (demanda de lotería), cartera mensual

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 71).

## Tesis (G0)
Los compradores de "lotería" pagan de más por las monedas con subidas diarias extremas;
largo los 5 perps (top 50) con menor MAX, corto los 5 con mayor; rebalanceo cada 4 semanas.
MAX30 = máximo retorno diario de 30 días; MAX5 = media de los 5 mayores.

## Evidencia (reports/h015_h016.json)
- G2 (2020–2022): MAX30 16,5 %/año, Sharpe 0,39, MDD −54 %; MAX5 18 %/año, Sharpe 0,41,
  MDD −62 %. IC95 semanal incluye 0 en ambas.
- G3 walk-forward 2023–2025: **1,5 %/año, Sharpe 0,04, MDD −59 %, IC95 [−0,85 %, +0,90 %]**;
  2023 −19 %, 2024 −6 %, 2025 +29 %.

## Por qué se rechaza
Sin señal in-sample ni OOS; drawdowns del 54–62 %. La literatura ya mostraba signo
inestable (Özdamar et al. 2021 encuentran el efecto contrario).

## Reproducibilidad
`python3 experiments/h015_h016_lowrisk.py`.
