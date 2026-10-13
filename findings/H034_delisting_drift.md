# H034 — Deriva tras el anuncio de deslistado spot (corto en el perp)

**Veredicto: RECHAZADA (eventos insuficientes y sin señal).** Fecha: 2026-10-13. Variantes: 2 (contador global: 126).

## Tesis (G0)
Tras el anuncio de deslistado spot, los tenedores siguen vendiendo; corto en el perp
desde el open del día siguiente durante N días (7 o 30). Fuente: anuncios públicos de
Binance (categoría 161, 440 avisos 2022-02 → 2026-10; 42 con formato "Binance Will
Delist <tokens> on <fecha>").

## Evidencia (reports/h034.json, reports/h034_events.csv)
Solo 22 tokens tenían perp USDT-M vivo al anunciarse el deslistado spot (1 en train,
21 en OOS): Binance suele deslistar el perp antes o a la vez.
| N | eventos OOS | media neta | mediana | t | liquidaciones del corto | p vs nulo |
|---|---|---|---|---|---|---|
| 7 días | 21 | +3,3 % | +8,7 % | 0,40 | 1 | 0,19 |
| 30 días | 21 | −8,1 % | −1,0 % | −0,73 | 3 | 0,80 |

## Por qué se rechaza
Muestra demasiado pequeña (G4 exige ≥ 100) y sin señal significativa; a 30 días los
squeezes (liquidación al doblar el precio) dominan. Coincide con la revisión de
literatura: la caída ocurre en minutos y después hay rebotes (ALPACA, BAKE, SLF, HIFI).

## Reproducibilidad
`python3 experiments/h034_delisting_drift.py` (anuncios guardados con hash).
