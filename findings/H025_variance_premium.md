# H025 — Prima de riesgo de varianza (DVOL² − RV²) como señal de timing

**Veredicto: RECHAZADA en G4.** Fecha: 2026-10-13. Variantes: 2 + 2 pruebas G4 (contador global: 101).

## Tesis (G0)
Una prima de varianza alta indica aversión al riesgo que se compensa con retornos
futuros. Largo (perp 1x) en BTC/ETH solo las semanas con VRP > mediana de 52 semanas.
RV de 7 o 30 días; DVOL de Deribit. Elegida en train: RV 7 días.

## Evidencia (reports/h025.json, reports/h025_g4_alts.json)
- G2 (2021-04 → 2022): RV7 +32,7 %/año frente a B&H −25 %; **alfa 49 %/año, IC95 > 0**.
- G3 (2023-01 → 2025-09, RV7): 44 %/año, Sharpe 1,23 (B&H 1,26), MDD −33 % (B&H −49 %),
  **alfa +15,8 %/año con beta 0,44, IC95 del alfa incluye 0**.
- G4: costes ×2 alfa +13,8 % ✓; vecino RV30 alfa +11,8 % ✓; alfa positivo 2023 (+13 %),
  2024 (+15 %), 2025 (+34 %) ✓; 111 cambios de posición ✓.
- **G4 otros activos (señal de BTC sin cambios en SOL, BNB, XRP): alfa −0,9 %, −3,3 %,
  −3,7 %/año; cartera Sharpe 0,87 frente a 1,56 de B&H, alfa −3,4 %.** ✗

## Por qué se rechaza
No funciona en activos no usados para diseñarla, y en BTC/ETH el alfa OOS no es
estadísticamente distinto de 0. Lo que sí hace de forma consistente es reducir el
drawdown (estar fuera la mitad del tiempo), pero eso es gestión de exposición, no una
ventaja demostrada.

## Qué se aprendió
- Es la señal de timing más consistente encontrada en BTC/ETH (alfa positivo en los 3
  años OOS y robusta a costes y al parámetro vecino), pero no se transmite a altcoins.
- Candidata razonable para el holdout 2025-10 → 2026-09 si en el futuro aparece una
  versión que pase G4; no se gasta el holdout en una hipótesis ya rechazada.

## Reproducibilidad
`python3 experiments/h025_vrp.py && python3 experiments/h025_g4_alts.py`.
