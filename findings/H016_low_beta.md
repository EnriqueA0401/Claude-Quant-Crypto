# H016 — Baja volatilidad / betting-against-beta, cartera mensual

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 71).

## Tesis (G0)
Los inversores con restricciones de apalancamiento sobrepagan activos de alta beta;
largo los 5 perps (top 50) de menor riesgo, corto los 5 de mayor; rebalanceo cada 4
semanas. Riesgo = volatilidad diaria de 30 días o beta frente a BTC de 60 días.

## Evidencia (reports/h015_h016.json)
- G2 (2020–2022): beta60 **40 %/año, Sharpe 1,23, MDD −26 %, IC95 semanal > 0**;
  vol30 3,5 %/año, Sharpe 0,08, MDD −65 %.
- G3 walk-forward 2023–2025 (beta60 en los 3 primeros folds, vol30 después):
  **−33 %/año, Sharpe −0,68, MDD −79 %**; 2023 −59 %, 2024 −59 %, 2025 +27 %.

## Por qué se rechaza
Negativa OOS con drawdown del 79 %. El resultado in-sample de beta60 (el mejor de esta
familia) es el quinto caso en que 2020–2022 da una señal "significativa" que se invierte
en 2023–2025 (tras H002, H005, H008, H013).

## Qué se aprendió
En 2023–2025 los pares de alta beta (memecoins, narrativas) subieron más que los de baja
beta: el factor beta se invirtió. Las anomalías de riesgo cross-sectional en cripto no
son estables entre regímenes.

## Reproducibilidad
`python3 experiments/h015_h016_lowrisk.py`.
