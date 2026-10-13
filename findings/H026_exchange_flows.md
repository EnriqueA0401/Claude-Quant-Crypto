# H026 — Entradas netas anómalas a exchanges (on-chain) → fuera del mercado 7 días

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 109).

## Tesis (G0)
Grandes tenedores mueven monedas a exchanges para vender; tras una entrada neta anómala
(z > k sobre 90 días, normalizada por la oferta en exchanges) conviene estar fuera 7 días.
Datos: Coin Metrics community (FlowInExNtv, FlowOutExNtv, SplyExNtv), perps BTC/ETH.

## Evidencia (reports/h026.json)
| k | periodo | %/año | Sharpe m. | MDD | B&H: %/año, Sharpe | alfa (beta) |
|---|---|---|---|---|---|---|
| 1,5 (elegida) | 2020–2022 | 54,3 % | 0,93 | −60 % | 70,8 %, 0,94 | +13,9 % (0,57) |
| 2 | 2020–2022 | 51,3 % | 0,74 | −61 % | 70,8 %, 0,94 | +0,8 % (0,71) |
| 1,5 (elegida) | **2023–2025** | **50,2 %** | **1,24** | **−41 %** | **64,5 %, 1,26** | **+9,0 % (0,64)** |
| 2 | 2023–2025 | 63,9 % | 1,47 | −43 % | 64,5 %, 1,26 | +13,2 % (0,79) |
IC95 del alfa diario incluye 0 en todos los casos.

## Por qué se rechaza
La variante elegida en train no mejora el Sharpe de buy & hold ni en train (0,93 frente
a 0,94) ni OOS (1,24 frente a 1,26); el alfa no es significativo. La variante k = 2 es
mejor OOS, pero elegirla ahora sería mirar el periodo de test.
Además, los flujos de Coin Metrics no son point-in-time (revisados a posteriori): el
sesgo favorece a la estrategia, y aun así no hay ventaja.

## Qué se aprendió
Los datos on-chain gratuitos sirven como descriptivos, pero no permiten backtests sin
sesgo de anticipación; cualquier señal on-chain necesitaría datos guardados en tiempo
real (G7) para validarse.

## Reproducibilidad
`python3 experiments/h026_exchange_flows.py` (descarga Coin Metrics con hash en el manifest).
