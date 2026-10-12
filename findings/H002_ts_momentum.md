# H002 — Momentum de series temporales en perps BTC/ETH

**Veredicto: RECHAZADA en G5.** Fecha: 2026-10-12. Variantes: 8 (contador global: 14).

## Tesis (G0)
Infrarreacción y herding: el signo del retorno de L días predice el siguiente día.
Variantes: L ∈ {7, 14, 28, 56} × {largo/corto, largo/plano}. Perps 1x, barras diarias
UTC (solo días con 24 h), señal al close, ejecución al open siguiente, funding real,
costes perp 0,10 % por lado.

## Evidencia
- G2 (train 2020–2022, reports/h002_g2.json): largo/plano con L = 14–56 da Sharpe mensual
  0,8–1,4 en ambos activos (meseta, no pico). MDD 40–60 %. El funding pagado por ir largo
  cuesta 13–20 %/año en ese periodo.
- G3 walk-forward 2021-12 → 2025-09 (reports/h002_g3.json): casi siempre se elige L = 28
  largo/plano. OOS **27 %/año**, Sharpe 0,66, MDD −42 %, 263 operaciones.
  Buy & hold en el mismo periodo: 25 %/año, Sharpe 0,42, MDD −69 %.
  Costes ×2: 24 %/año. Otros pares sin rediseñar: SOL +66 %, BNB +12 %, XRP +29 %/año.
  Por año: 2022 −9 % (B&H −81 %), 2023 +65 %, 2024 +24 %, 2025 +21 %.
- **IC95 bootstrap (bloques de 60 días) del retorno medio diario: [−0,03 %, +0,18 %]:
  incluye 0.**
- G5 (reports/h002_g5.json, semanal, dev completo): DSR = 0,92 con 14 pruebas
  (< 0,95); PBO = 0,54 (> 0,2); alfa frente a B&H = 15 %/año con beta 0,60, IC95 del
  alfa semanal [−0,15 %, +0,75 %]: incluye 0.

## Por qué se rechaza
Falla tres criterios de G5 a la vez: DSR, PBO y bootstrap. Lo que sí parece real es la
reducción del drawdown frente a buy & hold en mercados bajistas, pero eso es gestión de
riesgo de una exposición larga, no una ventaja estadística demostrada: el alfa frente a
B&H no es significativo. Con ~4 años OOS y un activo que sube, no se distingue de la beta.

## Qué se aprendió
- Las estrategias largo/plano en cripto heredan la deriva alcista del periodo; hay que
  medir siempre el alfa frente a buy & hold, no solo el retorno.
- El PBO de 0,54 indica que elegir la "mejor" L no generaliza: la meseta en train no
  implica orden estable entre variantes fuera de muestra.
- El funding de los largos (13–20 %/año en 2020–2021) es un coste grande para cualquier
  estrategia larga en perps; en spot no se paga (pero la comisión es mayor).

## Reproducibilidad
`python3 experiments/h002_tsmom.py && python3 experiments/h002_g3_walkforward.py &&
python3 experiments/h002_g5_stats.py`. Hashes: data_manifest.json; commit en cada JSON.
Protocolo: pasos 1–3 cubiertos por tests/test_backtest.py; pasos 4–7 no hicieron falta
porque la hipótesis se rechaza.
