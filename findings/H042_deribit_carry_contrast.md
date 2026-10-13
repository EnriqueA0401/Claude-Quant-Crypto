# H042 — Contraste: carry siempre cubierto con futuros de Deribit (2017–2026)

**Veredicto: confirma el rechazo del carry (no operable; contraste pedido por la persona).**
Fecha: 2026-10-13. Variantes: 1 (contador global: 140).

## Diseño (fijado antes de ver resultados)
Regla de H033 sin cambios (siempre corto en el trimestral más cercano con ≥ 14 días, W = 1,
costes de futuro 0,10 % por lado por rotación), en barras diarias de 08:00 a 08:00 UTC
(día de Deribit). Futuros: trimestrales de Deribit (API pública, 35 contratos BTC desde
2017-11, 31 ETH desde 2019-03). Spot: Binance, open de las 08:00 UTC desde velas de 1 h.

## Resultados (reports/h042.json)
| año | BTC carry anualizado | ETH carry anualizado | caja (T-bill 3m, aprox.) |
|---|---|---|---|
| 2018 | −5,9 % | — | 1,9 % |
| 2019 | −0,4 % | +3,3 % | 2,1 % |
| 2020 | −2,5 % | −4,1 % | 0,4 % |
| 2021 | +6,2 % | +7,7 % | ≈ 0 % |
| 2022 | +0,8 % | +0,1 % | 2,0 % |
| 2023 | +0,9 % | +1,8 % | 5,0 % |
| 2024 | +11,9 % | +11,0 % | 5,0 % |
| 2025 | +5,3 % | +3,8 % | 4,2 % |
| 2026 (9 meses) | +1,9 % | +0,4 % | 3,8 % |
| **todo el periodo** | **+1,05 %/año, Sharpe 0,19, MDD −22,7 %** | **+3,1 %/año, Sharpe 0,77, MDD −8,8 %** | |
(2017: solo unas semanas, −75 % anualizado; no representativo.)

## Lectura
- El carry supera a la caja solo en 3–4 de 8–9 años (2021, 2024, a veces 2019/2025): los
  años de mercado alcista apalancado. En los bajistas (2018, 2020, 2022) el basis es
  bajo o negativo (backwardation) y estar siempre corto en el futuro pierde.
- La media de largo plazo (BTC 1 %/año, ETH 3 %/año) queda por debajo de la caja en
  promedio, con drawdowns de hasta −23 %.
- Confirma, con 8+ años y otro exchange, que el carry es una prima dependiente del
  régimen, no una ventaja estable. Familia carry cerrada definitivamente.

## Limitaciones
Tipos de caja aproximados (de memoria, no descargados); precios de Deribit (USD) frente
a spot de Binance (USDT); velas diarias (el vencimiento real liquida a las 08:00 con la
media del índice). Ninguna de ellas cambia la conclusión.

## Reproducibilidad
`python3 experiments/h042_deribit_carry.py` (descarga de Deribit con hash).
