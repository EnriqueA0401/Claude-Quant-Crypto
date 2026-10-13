# H043 — Presión compradora agresiva (ratio taker-buy) cross-sectional semanal

**Veredicto: RECHAZADA en G5.** Fecha: 2026-10-13. Variantes: 2 (G2) + 3 G4 (contador global: 146).
**Mejor resultado cross-sectional del proyecto; no supera la corrección por pruebas múltiples.**

## Tesis (G0)
Ordenar los perps (top 50 por volumen, con deslistados) por el ratio taker_buy_quote /
quote_volume de los 7 días previos; largo los 5 con más compras agresivas y corto los 5
con menos (continuación) o al revés (reversión). Motor de H005 corregido (costes 0,15 %
por lado, funding, liquidación de cortos).

## Evidencia
- G2 (2020-04 → 2022, reports/h043.json): continuación 60 %/año, Sharpe 1,79, MDD −33 %,
  IC95 > 0; reversión −96 %/año (espejo).
- G3 walk-forward 2023-01 → 2025-09 (siempre "continuación"): **44,5 %/año, Sharpe 0,93,
  MDD −30 %; 2023 +39 %, 2024 +25 %, 2025 +58 %; IC95 semanal [−0,06 %, +1,94 %].**
- G4 (reports/h043_g4.json, 2023–2025):
  | prueba | %/año | Sharpe | por año |
  |---|---|---|---|
  | costes ×2 | 33,4 % | 0,69 | +28 / +13 / +50 % |
  | ventana 3 días | 22,5 % | 0,43 | +12 / −27 / +77 % |
  | ventana 14 días | 20,2 % | 0,37 | −5 / +3 / +57 % |
  | pares 51–100 (no usados) | 28,0 % | 0,91 | −1 / +45 / +33 % |
  Control de momentum (1 semana): correlación 0,71, beta 0,65, alfa +24 %/año con IC95
  semanal [−0,29 %, +1,21 %] (incluye 0).
- **G5 (reports/h043_g5.json): PSR 0,98; DSR ≈ 0 con las 146 pruebas (≈ 0,60 excluyendo la
  variante espejo de reversión); PBO 0,19 ✓; White Reality Check p = 0,096 ✗; IC95 del
  retorno semanal incluye 0 ✗.**

## Por qué se rechaza
Falla tres criterios de G5. Con 146 pruebas acumuladas, un Sharpe semanal de 0,13 en
143 semanas es compatible con el máximo esperado por azar; el bootstrap no excluye 0 y la
mitad del retorno se explica por el factor momentum.

## Qué se aprendió
- Es la primera señal cross-sectional que es positiva en los 3 años OOS y en un universo
  no usado (pares 51–100): el flujo agresivo de compra contiene algo más que momentum
  (alfa +24 %/año, no significativo).
- Con el holdout consumido, la única forma de confirmarla sería paper trading (G7) o
  esperar datos nuevos (> 2026-09); el marco exige pasar G5 antes, y no lo hace.

## Reproducibilidad
`python3 experiments/h043_taker_flow.py && python3 experiments/h043_g4.py &&
python3 experiments/h043_g5.py`. Test en tests/test_h005_h006.py.
