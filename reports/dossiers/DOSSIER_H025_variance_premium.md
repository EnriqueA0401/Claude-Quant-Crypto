# DOSSIER H025 — Prima de riesgo de varianza (DVOL) como señal para estar largo

Estado: **rechazada en G4 (otros activos)**. Guardada como la señal de timing más
consistente encontrada en BTC/ETH.

## 1. Tesis económica
Cuando la volatilidad implícita de las opciones (DVOL de Deribit) supera mucho a la
realizada, los compradores de protección pagan una prima por miedo; esa aversión al
riesgo se compensa con retornos futuros mayores del subyacente (Bollerslev, Tauchen y
Zhou 2009). Quién pierde: compradores de protección que sobrepagan en momentos de miedo.

## 2. Especificación exacta (fijada antes de ver resultados)
- **Datos:** DVOL diario de Deribit (API pública get_volatility_index_data, resolución
  86400, valor close del día; desde 2021-03-24), guardado en data/deribit/dvol_{BTC,ETH}.json
  con hash en el manifest. Perps USDT-M BTCUSDT y ETHUSDT, klines 1d y funding.
- **Señal (función experiments/h025_vrp.vrp_signal):** cada domingo d, al close:
  RV² = varianza de los retornos log diarios de los últimos 7 días (variante elegida;
  la otra, 30 días) × 365; IV² = (DVOL_d / 100)²; VRP = IV² − RV².
  Largo si VRP_d > mediana de los 52 domingos anteriores (mínimo 26; sin historia → largo).
- **Ejecución:** posición del lunes a domingo = señal del domingo anterior, ejecutada en
  el open del lunes (perp 1x, sin apalancamiento).
- **Costes:** 0,10 % por lado sobre |Δposición|; funding real (el largo paga).
- **Cartera:** 50 % BTC, 50 % ETH. Benchmark: perp 1x permanente (con funding).
- **Selección:** RV 7 frente a RV 30 elegida por Sharpe en train (2021-04 → 2022).
- **Métrica principal:** alfa frente a buy & hold (regresión diaria), IC95 por bootstrap
  de bloques de 30 días.

## 3. Resultados
### Train 2021-04 → 2022-12 (reports/h025.json, commit 9e0103b)
| variante | %/año | Sharpe m. | MDD | alfa/año | beta | IC95 alfa diario |
|---|---|---|---|---|---|---|
| RV7 (elegida) | +32,7 % | 0,69 | −52 % | **+49,1 %** | 0,66 | **[+0,00025, +0,00251]** |
| RV30 | +7,6 % | 0,16 | −52 % | +25,3 % | 0,71 | [−0,00046, +0,00196] |
| buy & hold | −25,0 % | −0,35 | −77 % | — | — | — |

### OOS 2023-01 → 2025-09
| variante | %/año | Sharpe m. | MDD | alfa/año | beta | IC95 alfa diario | exposición |
|---|---|---|---|---|---|---|---|
| **RV7 (elegida)** | **44,2 %** | **1,23** | **−33 %** | **+15,8 %** | 0,44 | [−0,00023, +0,00112] | 41 % |
| RV30 | 40,9 % | 1,35 | −22 % | +11,8 % | 0,45 | [−0,00037, +0,00098] | 39 % |
| buy & hold | 64,5 % | 1,26 | −49 % | — | — | — | 100 % |
Por año (RV7): 2023 estrategia 30,5 % vs B&H 81,6 % (alfa +13,1 %, beta 0,21);
2024 49,9 % vs 63,4 % (alfa +15,1 %, beta 0,55); 2025 54,8 % vs 42,9 % (alfa +34,4 %, beta 0,48).
Costes ×2: 42,2 %/año, Sharpe 1,17, alfa +13,8 %. Cambios de posición OOS: 111.

### G4 otros activos: señal de BTC sin cambios en SOL, BNB, XRP (reports/h025_g4_alts.json, commit cfe80ac)
| activo | %/año | Sharpe | B&H %/año (Sharpe) | alfa/año | beta |
|---|---|---|---|---|---|
| SOL | 56,8 % | 0,97 | 145,8 % (1,40) | −0,9 % | 0,40 |
| BNB | 22,9 % | 0,76 | 69,6 % (1,48) | −3,3 % | 0,37 |
| XRP | 26,3 % | 0,48 | 104,0 % (0,96) | −3,7 % | 0,29 |
| cartera | 35,3 % | 0,87 | 106,5 % (1,56) | −3,4 % | 0,36 |

## 4. Estado frente a los gates
| gate | estado |
|---|---|
| G0 | ✓ |
| G1 | ✓ (DVOL desde 2021-03; perps sin huecos) — falta verificar en paso 5 que el close diario de DVOL se conoce al cierre del día UTC |
| G2 | ✓ alfa in-sample significativo |
| G3 | ~ alfa OOS +15,8 %/año pero IC95 incluye 0 |
| G4 costes ×2, meseta, años, ≥ 100 ops | ✓ |
| G4 otros activos | **✗** (alfa negativo en SOL, BNB, XRP) |
| G5–G7 | no alcanzados |

## 5. Protocolo de revisión
- Pasos 1–3: tests/test_h005_h006.py::test_h025_vrp_signal_weekly_timing_and_no_lookahead
  (la señal solo cambia en domingos; alterar datos posteriores no cambia la señal pasada).
  Motor de PnL: el mismo esquema que H024 (posición = señal desplazada, costes sobre Δ).
- Pasos 4–6: **no realizados** (hipótesis rechazada antes de G5).

## 6. Riesgos y cuestiones abiertas
- Dependencia de una fuente externa (Deribit) y de un único índice; solo BTC y ETH.
- El alfa OOS no es significativo; con exposición media del 41 % el retorno absoluto es
  menor que el de buy & hold en un mercado alcista.
- Si se retomara: usar el holdout 2025-10 → 2026-09 UNA sola vez, contando la prueba.

## 7. Reproducibilidad
```
python3 experiments/h025_vrp.py        # descarga DVOL (hash en el manifest) y calcula G2/G3
python3 experiments/h025_g4_alts.py
```
