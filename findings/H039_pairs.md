# H039 — Arbitraje estadístico por pares cointegrados (perps USDT-M, diario)

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 134).

## Tesis (G0)
Cada 30 días, los 5 pares más cointegrados (ADF del spread de 90 días, correlación ≥ 0,7)
del top 20 por volumen; se opera la convergencia 30 días (entrada |z| > e, salida en z = 0).
e ∈ {2; 2,5}; costes 0,15 % por lado y pata; funding.

## Evidencia (reports/h039.json)
| e | periodo | %/año | Sharpe m. | MDD | por año |
|---|---|---|---|---|---|
| 2 | 2020-04 → 2022 | −13,8 % | −0,78 | −38,7 % | −15,3 / −22,1 / −0,5 % |
| 2,5 | 2020-04 → 2022 | −10,0 % | −0,59 | −34,6 % | −9,9 / −20,9 / +3,4 % |
| 2 | 2023–2025 | −8,0 % | −0,96 | −26,1 % | +3,2 / −16,0 / −9,2 % |
| 2,5 | 2023–2025 | −7,9 % | −1,02 | −24,4 % | +0,7 / −18,8 / −3,7 % |

## Por qué se rechaza
Negativa en todas las variantes y periodos: la cointegración de 90 días no persiste en
los 30 días siguientes (los spreads siguen divergiendo) y los 4 lados de costes por
operación agravan la pérdida.

## Limitación del protocolo
El motor de pares tiene test de la parte estadística (ADF) pero no un test de PnL a mano
(paso 1). Un error podría sesgar el resultado; se acepta el rechazo porque coincide con la
literatura reciente (pairs trading diario en cripto sin ventaja tras costes) y porque
ningún resultado positivo depende de este código.

## Reproducibilidad
`python3 experiments/h039_pairs.py`.
