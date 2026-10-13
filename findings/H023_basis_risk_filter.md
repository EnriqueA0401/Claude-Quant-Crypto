# H023 — Basis trimestral alto como filtro de riesgo (largo spot BTC/ETH si basis < b)

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 95).

## Tesis (G0)
Un basis alto refleja apalancamiento minorista y anticipa caídas (BIS WP 1087). Estar
largo en spot BTC/ETH solo cuando el basis trimestral anualizado < b debería mejorar el
Sharpe y dar alfa frente a buy & hold. b ∈ {10 %, 15 %}; costes 0,15 % por lado.

## Evidencia (reports/h023.json; cartera 50/50 BTC/ETH)
| b | periodo | %/año | Sharpe m. | MDD | B&H %/año, Sharpe, MDD | alfa (beta) |
|---|---|---|---|---|---|---|
| 10 % | 2021–2022 | −6,9 % | −0,14 | −58 % | 35,8 %, 0,45, −76 % | −25 % (0,51) |
| 15 % | 2021–2022 | 3,0 % | 0,05 | −66 % | 35,8 %, 0,45, −76 % | −18 % (0,58) |
| 15 % (elegida) | **2023–2025** | **59 %** | **1,28** | **−46 %** | **73 %, 1,41, −48 %** | **−2,4 % (0,84)** |
IC95 del alfa diario incluye 0 en todos los casos.

## Por qué se rechaza
In-sample el filtro empeora claramente a buy & hold (sale del mercado en los tramos
alcistas, cuando el basis es alto). OOS tampoco mejora el Sharpe ni da alfa.

## Qué se aprendió
En Binance el basis alto acompaña a las subidas más que anticipar caídas a 1 día de
horizonte; el resultado del BIS (riesgo de crash) no se traduce en una regla de timing
rentable con datos diarios.

## Reproducibilidad
`python3 experiments/h023_basis_filter.py`.
