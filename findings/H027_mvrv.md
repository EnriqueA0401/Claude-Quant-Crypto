# H027 — MVRV: fuera del mercado en la zona de euforia

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 111).

## Tesis (G0)
Con el precio muy por encima del coste medio on-chain (MVRV en su percentil p de 730
días), los tenedores con plusvalías venden; salir del mercado en esa zona debería mejorar
el Sharpe. p ∈ {0,8; 0,9}; spot BTC/ETH 50/50; costes 0,15 % por lado.

## Evidencia (reports/h027.json)
| p | periodo | %/año | Sharpe m. | MDD | B&H: %/año, Sharpe, MDD | alfa (beta) |
|---|---|---|---|---|---|---|
| 0,8 | 2020–2022 | 17,3 % | 0,29 | −74 % | 90,1 %, 1,15, −76 % | −42 % (0,66) |
| 0,9 (elegida) | 2020–2022 | 27,5 % | 0,42 | −76 % | 90,1 %, 1,15, −76 % | −41 % (0,76) |
| 0,9 (elegida) | 2023–2025 | 67,1 % | 1,57 | −42 % | 73,3 %, 1,41, −48 % | +7,8 % (0,81), n.s. |
| 0,8 | 2023–2025 | 52,6 % | 1,34 | −41 % | 73,3 %, 1,41, −48 % | +3,1 % (0,67), n.s. |
Exposición OOS 82 %, 76 cambios de posición.

## Por qué se rechaza
In-sample destruye valor (alfa −41 %/año): sale del mercado en plena subida de 2020–2021
(el MVRV alto puede durar meses). OOS la mejora del Sharpe no es significativa y no se
puede separar de la suerte de un periodo; la regla no sobrevive a su propio train.
Datos Coin Metrics no point-in-time (sesgo a favor), y aun así falla.

## Reproducibilidad
`python3 experiments/h027_mvrv.py`.
