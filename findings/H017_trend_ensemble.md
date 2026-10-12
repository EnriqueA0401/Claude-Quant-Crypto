# H017 — Tendencia multi-moneda largo/plano (ensemble Donchian, tamaño por volatilidad)

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 73).

## Tesis (G0)
Compradores tardíos y tenedores que no reducen riesgo pierden frente a una cartera de
tendencia diversificada (Zarattini, Pagani y Barbon 2025). Top 20 perps por volumen,
5 lookbacks Donchian con histéresis, peso = señal · min(1, 0,8 %/σ60) / 20, solo largos.

## Evidencia (reports/h017.json)
| variante | periodo | %/año | Sharpe m. | MDD | alfa vs BTC | beta |
|---|---|---|---|---|---|---|
| diaria (elegida en train) | 2020–2022 | 4,8 % | 0,95 | −7 % | +2,3 % | 0,04 |
| diaria | **2023–2025** | **4,5 %** | **0,76** | **−5 %** | **−1,7 %** | 0,08 |
| semanal | 2023–2025 | 3,8 % | 0,71 | −5 % | −2,8 % | 0,08 |
IC95 del alfa diario OOS incluye 0. Exposición media muy baja (el tamaño por volatilidad
deja la cartera casi siempre muy por debajo de 1x).

## Por qué se rechaza
Fuera de muestra no hay alfa: todo el retorno se explica por una pequeña exposición a
BTC en un periodo alcista. Además rinde menos que el efectivo (≈ 4–5 %/año).

## Qué se aprendió
El resultado publicado (alfa ~10 %/año en 2015–2025) no se reproduce en 2023–2025 con
perps de Binance, costes y funding. Confirma H002: la tendencia en cripto no tiene alfa
reciente frente a la simple exposición.

## Reproducibilidad
`python3 experiments/h017_trend_ensemble.py`. Test en tests/test_h005_h006.py.
