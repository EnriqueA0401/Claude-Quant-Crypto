# H011 — Cash-and-carry en altcoins (largo spot + corto perp)

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 4 (contador global: 53).

## Tesis (G0)
Los largos apalancados en altcoins pagan funding alto durante semanas; una cobertura
spot/perp lo cobra sin riesgo de precio. Predicción: ≥ 5 %/año sobre capital neto de
4 lados de costes, ≥ 100 entradas OOS. Cartera semanal: los 5 pares (top 50 por volumen,
con spot) de mayor funding equivalente a 8 h en D días; D ∈ {3, 7}, filtro θ ∈ {—, 3e-4}.

## Evidencia
- G2 (2020-04 → 2022-12; reports/h011_g2.json), tras correcciones: sin filtro θ el carry
  no paga los costes (−2,6 % y +0,1 %/año). Con θ: ~4,1–4,2 %/año, Sharpe 1,1–1,2,
  MDD 3–4 %, IC95 en el límite de 0. Ya por debajo del 5 % de la predicción.
- G3 walk-forward 2023-01 → 2025-09 (reports/h011_g3.json): siempre D = 7, θ = 3e-4.
  **OOS −2,6 %/año, Sharpe −0,47, MDD −9,4 %, IC95 incluye 0.** Funding +2,0 %,
  basis −3,4 %, costes −1,3 %. Solo ~51 entradas y 0,48 pares de media: casi siempre
  en liquidez. 2023 −9,1 %, 2024 +2,8 %, 2025 −0,9 %.

## Correcciones durante la prueba (pesimistas)
- Funding normalizado a 8 h (muchos pares liquidan cada 4 h o 1 h desde 2023).
- Barras con volumen 0 (pares suspendidos con precio plano) no operables.
- Liquidación del corto: el spot se cuenta como mucho +100 % y no se cobra el funding
  de esa semana (antes se contaba toda la subida del spot: ganancia por suerte).
- Desempate determinista de rankings (empates en el funding por defecto 0,01 %).

## Por qué se rechaza
Negativa OOS, por debajo del rendimiento de stablecoins y sin las 100 entradas exigidas.
Con θ alto apenas hay oportunidades; sin θ, los 4 lados de costes de altcoins
(≈ 0,5 % ida y vuelta) y los movimientos del basis se comen el funding.

## Qué se aprendió
- El funding alto de altcoins que cobraba H008 (~33 %/año en la pata corta) viene de
  pares sin spot en Binance o con basis muy volátil; con cobertura spot no se captura.
- Los resultados del carry son muy sensibles a la forma de medir el funding (intervalo)
  y a la liquidación: detalles que el revisor encontró y que cambiaban el signo.

## Reproducibilidad
`python3 experiments/h011_alt_carry.py && python3 experiments/h011_g3_walkforward.py`.
Tests: tests/test_h011.py (PnL a mano, cobertura, θ, anti-lookahead, nulo, liquidación).
