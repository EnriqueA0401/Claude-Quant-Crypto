# H004 — Rebote tras cascadas de liquidación (caída fuerte + OI cae)

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-12. Variantes: 4 (contador global: 46).

## Tesis (G0)
Los liquidados venden sin importar el precio; quien aporta liquidez en ese momento cobra
una prima. Evento: retorno 1h ≤ −k·σ (σ de 30 días previos) y ΔOI de la hora ≤ su
percentil 5 de 30 días. Largo 1x H horas. k ∈ {3, 4} × H ∈ {4, 24}.

## Evidencia (train 2020-09 → 2022-12; reports/h004_g2.json)
- Datos de OI (metrics 5 min de data.binance.vision): BTC desde 2020-09, ETH solo desde
  2021-12; 12 horas sin dato en BTC (se rellenan con el último valor).
| variante | ops | media/op | t | nulo | p vs nulo |
|---|---|---|---|---|---|
| BTC k=3 H=4 | 61 | −0,09 % | −0,24 | −0,20 % | 0,30 |
| BTC k=3 H=24 | 56 | +0,17 % | 0,24 | −0,15 % | 0,25 |
| BTC k=4 H=4 | 32 | −0,13 % | −0,24 | −0,20 % | 0,39 |
| BTC k=4 H=24 | 30 | −0,23 % | −0,21 | −0,15 % | 0,56 |
| ETH (4) | 15–25 | −0,3 % a −3,0 % | −0,7 a −1,9 | — | 0,66–0,99 |

## Por qué se rechaza
Ninguna variante tiene t > 0,25 ni bate al nulo de largos aleatorios (p ≥ 0,25); en ETH
el efecto va en contra (tras la cascada, sigue cayendo). No hay nada que llevar a G3.

## Qué se aprendió
- En barras de 1 h, la "capitulación" de liquidaciones no marca suelo de forma fiable:
  a menudo es el principio de la caída, no el final.
- Un rebote, si existe, sería en minutos (microestructura) y no compensaría 0,20 % de
  ida y vuelta con órdenes taker.

## Reproducibilidad
`python3 -c "from src.universe import download_metrics; download_metrics([...])"` y
`python3 experiments/h004_liq_rebound.py`. Señal: src/signals.liquidation_rebound_long (tests).
