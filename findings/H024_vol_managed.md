# H024 — Carteras gestionadas por volatilidad (BTC/ETH)

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 97).

## Tesis (G0)
Escalar la exposición por c/σ² (Moreira y Muir 2017) mejora el Sharpe porque la varianza
persiste más que la prima de riesgo. σ² realizada (30 días) o implícita (DVOL de
Deribit); w ≤ 1,5; rebalanceo semanal; perps con funding; 50/50 BTC/ETH.

## Evidencia (reports/h024.json)
| σ² | periodo | %/año | Sharpe m. | MDD | B&H: %/año, Sharpe, MDD | alfa (beta) |
|---|---|---|---|---|---|---|
| realizada | 2021-04 → 2022 | −42,7 % | −0,64 | −85 % | −25 %, −0,35, −77 % | −22 % (0,82) |
| DVOL | 2021-04 → 2022 | −44,6 % | −0,62 | −85 % | −25 %, −0,35, −77 % | −22 % (0,89) |
| DVOL (elegida) | 2023–2025 | 97 % | 1,28 | −65 % | 64,5 %, 1,26, −49 % | +2,3 % (1,47) |
| realizada | 2023–2025 | 94,5 % | 1,33 | −54 % | 64,5 %, 1,26, −49 % | +10,2 % (1,31) |
IC95 del alfa diario incluye 0 (o lo roza) en todos los casos.

## Por qué se rechaza
In-sample empeora a buy & hold con claridad (alfa −22 %/año). OOS el Sharpe es casi el
mismo que el de buy & hold: el retorno extra viene de más apalancamiento (exposición
media 1,48×, casi en el tope, porque la volatilidad 2023–25 fue menor que la de train).

## Qué se aprendió
En cripto la volatilidad alta coincide a menudo con subidas fuertes (2021): reducir
exposición cuando la volatilidad sube recorta los mejores tramos. El resultado de
Moreira y Muir (acciones) no se traslada a BTC/ETH.

## Reproducibilidad
`python3 experiments/h024_vol_managed.py` (descarga DVOL de Deribit con hash).
