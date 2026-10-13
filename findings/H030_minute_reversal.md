# H030 — Reversión tras minutos extremos (cota bruta)

**Veredicto: RECHAZADA (cota bruta insuficiente).** Fecha: 2026-10-13. Variantes: 4 (contador global: 119).

## Tesis (G0)
Órdenes de mercado grandes empujan el precio más allá de su valor; tras un minuto con
|retorno| > k·σ el precio revierte. Cota: si el rebote medio bruto no supera el coste
maker de ida y vuelta (0,04 %) con t > 3, no puede ser rentable.

## Evidencia (reports/h030.json; klines 1m BTC/ETH perp, 2022)
| activo | k | H | eventos | rebote medio bruto | t |
|---|---|---|---|---|---|
| BTC | 4 | 5 min | 3.311 | 0,014 % | 1,45 |
| BTC | 4 | 30 min | 3.311 | 0,013 % | 0,87 |
| BTC | 6 | 5 min | 1.006 | 0,040 % | 1,84 |
| BTC | 6 | 30 min | 1.006 | 0,055 % | 1,70 |
| ETH | 4 | 5 min | 3.094 | 0,015 % | 1,19 |
| ETH | 4 | 30 min | 3.094 | −0,001 % | −0,04 |
| ETH | 6 | 5 min | 885 | 0,049 % | 1,61 |
| ETH | 6 | 30 min | 885 | 0,011 % | 0,23 |

## Por qué se rechaza
Ningún caso supera la cota (0,04 % con t > 3). Los mejores (k = 6) igualan el coste maker
sin significación y suponen fills maker perfectos, sin selección adversa; con taker
(0,20 % ida y vuelta) serían claramente negativos. Coincide con la literatura (reversión
de 15 min: 1,3 pb brutos frente a 5 pb de coste).

## Reproducibilidad
`python3 experiments/h030_minute_reversal.py` (klines 1m de 2022, hash en el manifest).
