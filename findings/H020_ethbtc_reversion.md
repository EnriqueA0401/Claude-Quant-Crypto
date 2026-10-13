# H020 — Reversión del ratio ETH/BTC

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 83).

## Tesis (G0)
Las rotaciones entre BTC y ETH sobrerreaccionan; tras |z| ≥ k (90 días) la posición
neutral contraria gana al volver a la media (o en 30 días). k ∈ {2; 2,5}; perps,
0,5 por pata, costes 4 lados, funding.

## Evidencia (reports/h020.json)
| k | train: entradas, %/año, Sharpe, MDD | OOS: entradas, %/año, Sharpe, MDD |
|---|---|---|
| 2 | 11, −2,6 %, −0,20, −30 % | 18, −5,4 %, −0,32, −36 % |
| 2,5 | 8, −2,6 %, −0,17, −25 % | 11, −4,4 %, −0,42, −18 % |
(OOS calculado en la misma ejecución; no se usó para decidir.)

## Por qué se rechaza
Negativa in-sample y con muy pocas operaciones. El ratio ETH/BTC tiene tendencias
largas (ETH perdió frente a BTC de forma persistente en 2022–2025): apostar por la
reversión pierde.

## Reproducibilidad
`python3 experiments/h020_ethbtc.py`. Test en tests/test_h005_h006.py.
