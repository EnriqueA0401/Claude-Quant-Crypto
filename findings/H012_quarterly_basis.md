# H012 — Basis de futuros trimestrales fijado a la entrada

**Veredicto: RECHAZADA en G4.** Fecha: 2026-10-13. Variantes: 4 + 2 vecinos (contador global: 67).

## Tesis (G0)
Comprar spot y vender el trimestral cuando el basis anualizado > θ fija ese rendimiento
hasta el vencimiento (o hasta que el basis se colapse: salida anticipada si < θ/4).
θ ∈ {5 %, 10 %} × {vencimiento, anticipada}. 1x, w = 0,5 por pata, costes 4 lados.

## Evidencia
- G2 (BTC/ETH, vencimientos 2021–2022; reports/h012_g2.json): 1–4 %/año sobre capital,
  6–15 %/año sobre capital desplegado (variantes con salida anticipada), MDD 3,5–7 %,
  5–19 entradas en 2 años.
- **G3 walk-forward 2023-01 → 2025-09 (reports/h012_g3.json): siempre θ = 5 %, anticipada.
  OOS 3,6 %/año sobre capital, Sharpe 1,73, MDD 2,2 %, IC95 > 0, positiva 2023, 2024 y
  2025. Solo 24 entradas.** Primera hipótesis que supera G3.
- Paso 4 (reports/h012_protocol.md): reimplementación independiente idéntica en 7/8
  combinaciones; la octava, explicada por horas de mantenimiento del spot (la nuestra es
  la correcta y la más pesimista).
- **G4 (reports/h012_g4.json): misma regla, sin rediseño, en los trimestrales COIN-M de
  12 monedas no usadas (ADA, BCH, BNB, DOT, EOS, ETC, FIL, LINK, LTC, SOL, TRX, XRP),
  capital repartido a partes iguales:**
  | prueba | %/año | Sharpe | MDD | 2023–2025 |
  |---|---|---|---|---|
  | base (θ 5 %) | −1,0 % | −0,39 | −14,5 % | −5,3 %/año |
  | costes ×2 | −7,3 % | −1,37 | −45,6 % | −20,3 %/año |
  | vecino θ 3 % | −3,5 % | −1,05 | −28,9 % | −10,7 %/año |
  | vecino θ 7 % | +0,1 % | 0,06 | −7,6 % | −2,5 %/año |
  Por moneda: positivas BCH (+5,5 %), BNB (+1,5 %); negativas DOT (−17,8 %), LINK, SOL,
  LTC, ADA. 2.332 entradas: el basis de los trimestrales de altcoins supera θ a menudo
  pero no converge de forma rentable (contratos poco líquidos, precios con saltos).

## Por qué se rechaza
G4 exige que funcione en activos no usados para diseñarla y ≥ 100 operaciones OOS. En
BTC/ETH hay solo 24; en las 12 altcoins la misma regla pierde, y con costes ×2 pierde
mucho. Lo positivo de BTC/ETH es real pero pequeño (3,6 %/año, por debajo del
rendimiento de stablecoins) y no generaliza.

## Qué se aprendió
- El carry fijado en BTC/ETH es la señal más limpia encontrada: positiva fuera de
  muestra los 3 años, con drawdown mínimo. Pero rinde menos que una cuenta de ahorro en
  USDT y no tiene suficientes operaciones para validarse estadísticamente.
- En altcoins, el basis "alto" de los trimestrales es en buena parte ruido de liquidez.

## Reproducibilidad
`python3 experiments/h012_quarterly_basis.py`, `h012_g3_walkforward.py`,
`h012_g4_robustness.py`. Tests: tests/test_h012.py. Motor acelerado con numpy
(resultados idénticos comprobados).

## Revisión por checklist (paso 5) y re-ejecución — 2026-10-13
El revisor encontró un error grave de datos: varios ficheros de trimestrales siguen
semanas después del vencimiento con barras congeladas (0 operaciones). El motor tomaba
el vencimiento del final de los datos, así que entraba en contratos ya liquidados
(BTC/ETH 230929 en octubre de 2023), con la pata spot sin cubrir. También señaló que
los trimestrales COIN-M de altcoins tienen un 6–54 % de barras sin operaciones.
Corregido: corte en el vencimiento programado (YYMMDD 08:00 UTC), barras sin
operaciones excluidas de señal y fills, y último precio negociado si la posición está
abierta (tests en tests/test_h012.py).
- **G3 corregido: OOS 3,30 %/año, Sharpe 1,56, MDD −1,1 %, IC95 > 0, 18 entradas.**
- Rendimiento sobre capital desplegado ≈ 4,1–4,8 %/año: **no cumple la predicción de G0
  (≥ 5 %)** y no supera al efectivo/USDT en 2023–2025 (≈ 4–5 %). Exceso sobre caja ≤ 0.
- Con cobertura de unidades iguales (en vez de nocional igual) el Sharpe baja a ~1,4.
- Capital pequeño: el lote mínimo del trimestral BTC (0,001 BTC ≈ 100 USD) deja hasta
  un 20 % de error de cobertura con 250 USD por pata; no modelado.
Veredicto sin cambios: rechazada. Lección para G1: validar siempre la última barra de
un futuro contra su fecha de vencimiento y el número de operaciones por barra.
- **G4 re-ejecutado con datos limpios (12 altcoins COIN-M): base -1.4 %/año,
  Sharpe -0.58, MDD -14.7 %, 2023–2025 -5.4 %/año;
  costes ×2 −5,9 %/año.** Sigue sin generalizar.
