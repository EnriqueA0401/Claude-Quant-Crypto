# H031 — Cambio de intervalo de funding como señal de apalancamiento extremo

**Veredicto: RECHAZADA en G2/G3.** Fecha: 2026-10-13. Variantes: 2 (contador global: 121).

## Tesis (G0)
Cuando Binance acorta el intervalo de funding de un perp (8 h → 4 h/1 h) es porque el
funding es extremo; operar contra el lado que paga durante N días ganaría.
N ∈ {3, 7}; universo completo USDT-M; costes 0,15 % por lado; funding; nulo aleatorio.
Train 2023-01 → 2024-06 (los eventos casi no existían antes); OOS 2024-07 → 2025-09.

## Evidencia (reports/h031.json)
| N | periodo | eventos | media neta | mediana | t | p vs nulo |
|---|---|---|---|---|---|---|
| 3 | train | 47 | +1,8 % | +0,2 % | 0,52 | 0,15 |
| 7 (elegida: mayor t) | train | 47 | +2,4 % | +1,7 % | 0,57 | 0,22 |
| 3 | OOS | 70 | +10,9 % | +1,8 % | 2,13 | 0,05 |
| 7 | OOS | 70 | +33,0 % | +1,7 % | 1,26 | 0,00 |
La media OOS la dominan unos pocos eventos: ALPACA (largo tras funding negativo,
2025-04-24) +1.805 % en 7 días (squeeze tras el anuncio de deslistado), IP +212 %,
AERGO +123 %, MYX +120 %. **Sin los 3 mayores: media +2,5 %, t = 0,65.**

## Por qué se rechaza
In-sample no hay señal (t ≈ 0,5). OOS la media depende de squeezes extremos de pares
pequeños, no replicables ni con capacidad real (liquidez, límites de posición, riesgo de
deslistado). Menos de 100 eventos en cada periodo.

## Qué se aprendió
El acortamiento del intervalo de funding coincide con episodios de squeeze en pares
pequeños: el riesgo de cola del lado corto es enorme. No es una ventaja sistemática.

## Reproducibilidad
`python3 experiments/h031_funding_interval.py`. Test en tests/test_h005_h006.py.
