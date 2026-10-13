# DOSSIER H022 — Carry trimestral COIN-M BTC/ETH con la moneda como margen

Estado: **RECHAZADA en G5 tras el red team (2026-10-13)**. Antes: reabierta por excepción de la persona responsable: se exime
SOLO del mínimo de 100 operaciones OOS de G4, estructuralmente inalcanzable para un carry
trimestral. El resto de criterios se mantiene; ver "Estado frente a los gates".

## 1. Tesis económica
Los largos apalancados con vencimiento (trimestrales) pagan una prima (basis) sobre el
spot. Comprar la moneda y vender el trimestral inverso COIN-M por el mismo valor fija ese
basis hasta el vencimiento. Con la moneda como margen del corto, todo el capital está en
la cobertura y el corto no puede liquidarse (el margen sube con el precio).
Quién pierde: demanda de apalancamiento largo con vencimiento; arbitraje con capital
escaso.

## 2. Especificación exacta (fijada antes de ver resultados)
- **Instrumentos:** Binance COIN-M trimestrales BTCUSD_YYMMDD y ETHUSD_YYMMDD (inversos;
  contrato = 100 USD en BTC, 10 USD en ETH). Pata spot: BTCUSDT y ETHUSDT.
- **Datos:** klines 1h de data.binance.vision (futures/cm monthly + daily; spot monthly),
  índice = open time UTC. 21 contratos por activo.
- **Limpieza (G1):** cada contrato se corta en su vencimiento programado (YYMMDD 08:00
  UTC; último bar 07:00). Barras con 0 operaciones → NaN (sin señal ni fill). Spot con
  huecos de mantenimiento: se mide en los mismos instantes que el futuro.
- **Selección de contrato:** al close de cada hora sin posición, el primer contrato (orden
  por nombre = cronológico) con ≥ 14 días hasta su último bar y close no NaN.
- **Señal:** basis anualizado = (F_close / S_close − 1) · 365 / días restantes.
  Entrada en el open de la hora siguiente si basis > θ = 5 %.
- **Salida:** al close de una hora con posición, si basis anualizado < θ/4 = 1,25 % →
  salida en el open siguiente; si no, al vencimiento (futuro al close de su último bar,
  spot en el open siguiente).
- **Tamaño:** W = 1 por pata (capital completo en moneda; corto por el mismo valor).
  Unidades fijas desde la entrada; PnL del bar = W·(ΔS/S_ref − ΔF/F_ref) (aproximación
  lineal en USD del contrato inverso; error de segundo orden).
- **Rebalanceo:** si el futuro se aleja > 25 % de la referencia: coste W·|mov|·(cs+cf) y
  nuevas referencias.
- **Liquidación:** no aplica (corto cubierto con margen en moneda).
- **Costes por lado:** spot 0,10 % comisión + 0,05 % slippage; futuro 0,05 % + 0,05 %.
  Se cobran en entrada, salida anticipada y vencimiento (más que la comisión de entrega).
- **Cartera:** 50 % BTC, 50 % ETH. Capital ocioso al 0 %.
- **Parámetros:** θ = 5 % y salida anticipada, elegidos por walk-forward en H012-G3
  (BTC/ETH USDT-M) antes de aplicarse a COIN-M; no se reoptimizaron.

## 3. Resultados
### OOS 2023-01-01 → 2025-09-30 (reports/h022.json, commit e33fa1a)
| métrica | valor |
|---|---|
| retorno anual sobre capital | **6,37 %** (BTC 6,57 %, ETH 6,17 %) |
| Sharpe (mensual anualizado) | **1,35** |
| drawdown máximo | **−2,64 %** |
| IC95 del retorno horario medio | [3,6e-6, 1,16e-5] (> 0) |
| por año | 2023 +2,33 % · 2024 +12,35 % · 2025 (9 meses) +2,84 % |
| tiempo invertido | BTC 93,9 %, ETH 88,7 % |
| entradas | BTC 16, ETH 15 (31) |
| costes | ≈ 3,1 %/año |
| benchmark USDT | 5 %/año → lo supera en ≈ 1,4 %/año |
Train 2021–2022: 5,0 %/año (BTC 5,2 %, ETH 4,7 %).

### G4 (reports/h022_g4.json, commit 6b8cf94)
| prueba | %/año OOS | Sharpe | MDD | entradas | por año |
|---|---|---|---|---|---|
| θ 3 % (vecino) | 6,11 % | 1,29 | −2,6 % | 31 | +1,8 / +12,3 / +2,7 % |
| θ 7 % (vecino) | 6,36 % | 1,34 | −2,6 % | 26 | +2,3 / +12,3 / +3,0 % |
| costes ×2 | 3,28 % | 0,63 | −3,1 % | 31 | −1,6 / +10,1 / +0,5 % |
| 12 altcoins COIN-M (ADA, BCH, BNB, DOT, EOS, ETC, FIL, LINK, LTC, SOL, TRX, XRP) | −10,8 % | −1,70 | −26,3 % | 1.345 | −7,9 / −1,7 / −20,1 % |

### Antecedentes (misma regla, USDT-M, W = 0,5; H012)
G3 walk-forward OOS: 3,30 %/año, Sharpe 1,56, MDD −1,1 %, 18 entradas (reports/h012_g3.json).

## 4. Estado frente a los gates
| gate | estado |
|---|---|
| G0 | ✓ escrito antes de ver datos (HYPOTHESES.md) |
| G1 | ✓ tras corregir vencimientos y barras sin operaciones |
| G2 | ✓ (train 5,0 %/año) |
| G3 | ✓ OOS 6,4 %/año, IC95 > 0, > USDT |
| G4 costes ×2 | ✓ literal (3,3 %/año > 0), pero < USDT y 2023 negativo |
| G4 meseta | ✓ θ 3–7 % igual |
| G4 regímenes / años | ✓ 3 de 3 años positivos (2022 bajista solo en train: +) |
| G4 otros activos | ✗ altcoins COIN-M −10,8 %/año (contratos ilíquidos) |
| G4 ≥ 100 operaciones | **eximido por la persona responsable** (31) |
| G5 | ✗ — ver sección 9 (pasa DSR, White RC y bootstrap frente a 0; falla PBO; frente a caja falla todo) |
| G6 | pendiente (tamaño de contrato, capital < 1.000 USD) |
| G7 | pendiente |

## 5. Protocolo de revisión
- Pasos 1–3: tests/test_h012.py (PnL a mano con convergencia, liquidación, sin entrada
  bajo θ o < 14 días, salida anticipada, anti-lookahead, nulo, limpieza de contratos).
- Paso 4: reimplementación independiente del motor (reports/h012_protocol.md): 7/8
  idénticas; la octava explicada (horas de mantenimiento del spot).
- Paso 5: revisión por checklist (findings/H012_quarterly_basis.md): contratos vencidos y
  barras muertas corregidos; resto OK.
- Paso 6 (red team): hecho, ver sección 10. Paso 7: comandos abajo.

## 6. Riesgos y aspectos no modelados
- Contrato inverso modelado linealmente; USDT ≠ USD.
- Tamaño mínimo: 1 contrato = 100 USD (BTC) / 10 USD (ETH); con < 1.000 USD el error de
  cobertura por redondeo puede ser del 5–20 %.
- Riesgo de contraparte/exchange; rendimiento de USDT variable (el listón del 5 % puede
  subir o bajar).
- Cobertura que deriva cuando el precio sube (rebalanceo aproximado con banda del 25 %).
- Pocas operaciones independientes (≈ 8 rotaciones/año): IC frágil.

## 7. Reproducibilidad
```
python3 -m src.universe          # (universo) + descargas COIN-M BTC/ETH 1h (ver STATE/journal)
python3 experiments/h022_cm_carry.py
python3 experiments/h022_g4.py
```
Datos: data_manifest.json (grupos futures/cm/* y spot/monthly/klines/BTCUSDT, ETHUSDT) y
data_manifest_files.json.gz. Código: experiments/h012_quarterly_basis.py (motor),
experiments/h022_*.py.

## 8. Ejecución práctica (si llegara a G7)
1. Comprar BTC (y ETH) en spot por el 50 % del capital cada uno; transferir a la cuenta
   COIN-M como margen.
2. Cuando el basis anualizado del trimestral con ≥ 14 días supere el 5 %, vender
   contratos por el valor en USD de la moneda depositada.
3. Cerrar si el basis cae bajo 1,25 % anual; si no, dejar vencer y repetir con el
   siguiente contrato.
4. Ajustar contratos si el precio se mueve > 25 % desde la última referencia.

## 9. G5 (reports/h022_g5.json; retornos semanales, OOS 2023-01 → 2025-09)
Familia evaluada: θ ∈ {3, 5, 7 %} × {salida anticipada, vencimiento}, cartera 50/50.
Contador global usado en el DSR: 103 pruebas.

| criterio (CLAUDE.md) | frente a 0 (literal) | frente a caja 5 %/año | umbral |
|---|---|---|---|
| Deflated Sharpe | **0,992** ✓ | 0,598 ✗ | > 0,95 |
| PSR | 0,998 | 0,711 | — |
| PBO (CSCV, 6 variantes) | 0,51 ✗ | 0,51 ✗ | < 0,20 |
| White Reality Check (p) | **0,002** ✓ | 0,248 ✗ | < 0,05 |
| IC95 bootstrap (bloques 13 semanas) | [+0,057 %, +0,198 %]/semana ✓ | [−0,039 %, +0,101 %] ✗ | > 0 |
| retorno anual | 6,37 % | +1,28 % de exceso | — |

Lectura: el carry es un retorno positivo real y estadísticamente sólido frente a 0, pero
su exceso sobre el rendimiento de la caja (≈ 1,3 %/año) no es distinguible de 0. El PBO
de 0,51 refleja que las 6 variantes son casi idénticas (elegir la "mejor" en train no
predice cuál será mejor fuera): con el criterio literal, G5 no se supera.

## 10. Red team (paso 6) y respuesta por escrito a cada objeción
Subagente con instrucción explícita de REFUTAR (scripts en el scratchpad de la sesión).

| # | objeción (gravedad) | respuesta |
|---|---|---|
| 1 | Exceso sobre caja ≈ +1,5 %/año, Sharpe del exceso 0,33, DSR ≈ 0,04–0,6 (fatal) | **Aceptada.** Coincide con nuestro G5: DSR del exceso 0,60, IC95 del exceso incluye 0. |
| 2 | Depende de 2024 y en gran parte de 2024-T2 (+6,97 %); sin ese trimestre ≈ 4,2 %/año < caja; IC95 trimestral [2,7 %, 12 %], P(< 5 %) ≈ 30 % (fatal) | **Aceptada.** 2023 (+2,3 %) y 2025 (+2,8 % en 9 meses) quedan por debajo de la caja; la ventaja es episódica (picos de basis en mercados alcistas apalancados). |
| 3 | El OOS no es evidencia nueva: mismo periodo y subyacentes que H012-G3 (correlación mensual 0,965); θ y salida elegidos ahí (mayor) | **Aceptada.** H022 es H012 con doble tamaño; la única prueba limpia sería el holdout (~8 operaciones, sin potencia estadística). |
| 4 | El listón real se mueve con el carry: en 2024 el USDT Earn de Binance pagó ≈ 6 % (mayor) | **Aceptada como agravante** (fuente no oficial); refuerza la objeción 2. |
| 5 | G4 no se supera ni con la excepción: otros activos −10,8 %/año, costes ×2 < caja (mayor) | **Aceptada**; ya estaba registrado en la sección 4. |
| 6 | La aproximación lineal es correcta (±0,03 %/año frente a contabilidad exacta coin-margined); el rebalanceo del motor resta ≈ 1,2 %/año, pero ese extra es beta, no alfa (menor) | **Aceptada.** Valida el motor; no cambia el veredicto. |
| 7 | El precio de liquidación debería ser la media del índice de 30 min, no el último trade (sesgo ≈ −0,3 %/año en contra) (menor) | **Aceptada.** Pendiente para cualquier uso futuro: liquidar a la media del índice. |
| 8 | Tamaño de contrato resoluble (comprar spot igual al nocional de contratos; ≈ 1 % de lastre) (menor) | **Aceptada.** |
| 9 | Costes probablemente conservadores (rota spot en cada ciclo; una operativa real solo rotaría el corto) (menor) | **Aceptada.** Aun así, con costes ≈ 3,1 %/año la mejora posible (≈ 1–1,5 %/año) no cambia la conclusión frente a caja con la evidencia disponible. |
| 10 | Riesgos operativos: concentración en Binance, USDT frente a USD (menor) | **Aceptada.** |

## 11. Veredicto final
**Rechazada en G5.** El basis carry existe y la contabilidad es correcta, pero su exceso
sobre la caja (≈ 1,3–1,5 %/año) no es estadísticamente distinguible de 0, depende de un
episodio (2024-T2), el OOS no es independiente de H012, y G4 falla en otros activos y con
costes ×2. Con el criterio literal (frente a 0) también falla por PBO = 0,51.
Recomendación: no gastar el holdout 2025-10 → 2026-09 en validarla (≈ 8 operaciones, sin
potencia); si la persona lo desea, usarlo solo como comprobación descriptiva, una vez.
