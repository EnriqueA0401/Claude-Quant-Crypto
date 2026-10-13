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

## Addendum 2026-10-13 — validación complementaria, revisión y cierre DEFINITIVO
Autorizado por la persona responsable: holdout por hipótesis y validación sintética que
conserve la estructura. Pre-registrado en HYPOTHESES.md antes de ejecutar (contador 148).
- Permutación (señal barajada entre los mismos pares cada semana, retornos reales):
  p cont_7d 0,0025; p familia 0,0045 ✓ (reports/h043_validation.json).
- Holdout 2025-10 → 2026-09 (cont_7d, una vez): +101 %/año, Sharpe 1,32, MDD −50 %,
  IC95 semanal [−0,99 %, +4,76 %] (incluye 0); funding +66 %/año del bruto 112 %.
- Protocolo paso 4 (reimplementación por eventos, subagente que no vio el código): coincide
  exactamente (1,0103 vs 1,0103; OOS 0,443). Datos sin saltos ni prints erróneos; funding
  real en el tope −2 %/intervalo durante squeezes. reports/h043_reimpl_weekly.csv.
- Protocolo paso 6 (red team; scripts en experiments/h043_review/redteam/, leen un panel
  exportado a scratch → no reproducibles con un solo comando, solo archivados):
  1. Momentum 1 semana (H005, rechazada) gana +99 %/año en el mismo holdout; nulo que
     conserva el momentum (permutación dentro de deciles) → p holdout 0,074. Señal
     residualizada sobre momentum: +5,6 %/año OOS.
  2. Colas: OOS sin top-3 símbolos +4,6 %/año (≈ caja), sin top-10 semanas −6,4 %;
     holdout sin top-3 semanas −6 %, sin top-3 símbolos −47 %. PIPPIN aporta 0,75 de 0,99.
     Una operación OOS (ALPACA, squeeze de deslistado, +570 %) aporta ~21 de los 44 puntos.
  3. El racional G0 (flujo nuevo de esta semana) queda falsado: el score menos su media
     propia de 8 semanas da +0,3 %/año OOS; la media retrasada sola da +27 %/año. Es una
     inclinación estática hacia monedas minoristas propensas a squeezes, no flujo.
  4. Pruebas múltiples: Šidák sobre ~44 hipótesis → p ≈ 0,18; sobre 148 pruebas ≈ 0,49.
  5. Holdout no ciego: el conocimiento del modelo llega a 2026-06 (sabía de los pumps).
  6–7. Funding dependiente del régimen; MDD −50 % inviable para G6.
  9–12 (menores): ejecución realista a este tamaño, sin lookahead ni supervivencia.
### Respuesta a las objeciones
Acepto 1–7. Las objeciones 1 y 3 son fatales para la tesis: lo que la permutación detecta
es momentum más una inclinación estática a memecoins, ya probadas o sin racional de flujo.
La 2 muestra que el resultado es una lotería de colas (mediana semanal −0,3 %). La 5 invalida
el holdout como prueba ciega. No hay respuesta que las rebata.
### Veredicto final
**RECHAZADA definitivamente.** No pasa a G7. El "aprobado" pre-registrado de permutación y
holdout no resiste la revisión: la señal no es distinguible del momentum y depende de 3–5
eventos. Lección: un nulo de permutación debe conservar los factores conocidos (momentum),
y un estadístico recortado debe acompañar a la media en distribuciones con colas.
