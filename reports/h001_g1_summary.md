# H001 · G1 (datos) — 2026-10-12

Fuente: data.binance.vision, klines 1h spot y USDT-M + fundingRate, 2020-01 → 2026-09.
Hashes en data_manifest.json. Detalle: reports/h001_g1_data.json (experiments/h001_g1_data.py).

- Duplicados: 0 en todas las series. OHLC incoherente: 0. Precios ≤ 0: 0.
- Perps: 0 huecos tras rellenar con ficheros diarios los meses truncados
  (SOL y XRP: 2022-02-26/28 y 2022-04-01/02 faltaban en los mensuales).
- Spot: 19–31 horas sin datos por par, en tramos de 1–5 h (mantenimientos de Binance
  2020–2023). Son huecos reales del mercado: se rellenan con el último precio (retorno 0)
  y no se permite operar en esas horas.
- Funding: intervalo de 8 h en BTC/ETH/BNB/XRP; SOL tuvo 98 intervalos de 2 h y 3 de 4 h.
  El backtester suma cada evento real, sea cual sea el intervalo.
- Timestamps: UTC, índice = open time; spot 2025+ en microsegundos (tratado y testeado).
- Supervivencia: los 5 pares son supervivientes. SESGO ABIERTO: el test entre activos
  de G4 debe incluir perps deslistados (p. ej. LUNA, FTT, SRM) antes de dar G4 por bueno.

Veredicto: G1 superado para BTC/ETH (diseño) con la salvedad de supervivencia anotada.
