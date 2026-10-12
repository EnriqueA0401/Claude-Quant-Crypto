# H001 — Cash-and-carry spot/perp (largo spot + corto perp, 1x)

**Veredicto: RECHAZADA en G4.** Fecha: 2026-10-12. Variantes probadas: 6 (contador global: 6).

## Tesis (G0, escrita antes de ver datos)
Los largos apalancados pagan funding; una cobertura delta-neutral lo cobra. Entrada si la
media de las últimas k tasas > θ, salida si < θ/2. θ ∈ {1e-4, 2e-4, 3e-4}, k ∈ {1, 3}.
Costes: spot 0,10% + 0,05% slippage, perp 0,05% + 0,05% por lado (4 lados por ciclo).

## Evidencia
- G1 OK (reports/h001_g1_summary.md). Sesgo de supervivencia sin resolver (no llegó a importar).
- G2 (train 2020–2022, reports/h001_g2.json): θ ≤ 2e-4 → ~7–9 %/año sobre capital, Sharpe
  mensual anualizado 2,1–2,4 (3,6–3,9 si se anualiza por hora: inflado), MDD 1–2 %, solo 6–11 entradas en 3 años. θ = 3e-4 entra y sale demasiado.
- Bug encontrado y corregido: la liquidación usaba el high del último precio; una mecha de
  ETH (2020-03-13, 323 USDT) liquidaba falsamente. Ahora usa el mark price.
- Paso 4 del protocolo: reimplementación independiente por eventos
  (experiments/h001_independent.py) coincide con diferencia máxima 0,002 %.
- G3 walk-forward 2021-12 → 2025-09, 6 folds, embargo 1 semana (reports/h001_g3.json):
  siempre se elige θ = 1e-4, k = 3. Retorno OOS **1,4 %/año** sobre capital, Sharpe
  mensual 1,4, MDD 0,4 %. Con costes ×2: 1,0 %/año (Sharpe 0,9).
  IC95 bootstrap (bloques de 2 meses) del retorno medio > 0.
- Por año (suma de retornos OOS): 2022 +0,03 %, 2023 +1,3 %, 2024 +4,1 %, 2025 +0,00 %.
- Otros pares sin rediseñar: SOL +1,4 %/año (Sharpe 1,1), XRP +1,6 % (1,2), BNB −1,2 % (−1,9).

## Revisión por checklist (paso 5)
Sin errores que inflen el PnL. Corregido tras la revisión: Sharpe calculado con sumas
mensuales (metrics.sharpe_resampled), bootstrap con bloques de 2 meses, coste de
rebalanceo proporcional al movimiento real, cierre forzoso con coste al final de la
serie, paso de barra fijo de 1 h en la señal y funding tras el último open ignorado.
Pendiente (bajo impacto, sesgo mixto): nocional constante por barra en vez de unidades
fijas entre rebalanceos; umbral de liquidación aproximado (pesimista).

## Por qué se rechaza (G4)
1. Solo 13 entradas OOS (BTC 7, ETH 6) frente a un mínimo de 100.
2. El beneficio depende de un solo régimen (bull 2023-11 → 2024-07). En 2022 y 2025 es ~0:
   en la práctica no es rentable en 2 de cada 3 años.
3. Falla en uno de tres pares no usados para el diseño (BNB).
4. Viabilidad económica: 1,4 %/año (≈14 USD/año con 1.000 USD) está por debajo del
   rendimiento de dejar el dinero en stablecoins. No es una ventaja explotable.

## Qué se aprendió
- El Sharpe alto del carry viene de una volatilidad casi nula, no de un retorno grande.
  Hay que juzgar el retorno absoluto frente al coste de oportunidad.
- Nunca anualizar el Sharpe de barras horarias con retornos autocorrelacionados: usar
  metrics.sharpe_resampled (mensual) en todos los experimentos.
- Desde 2022 el funding de BTC/ETH pasa la mayor parte del tiempo en el 0,01 % por defecto
  (~11 %/año sobre nocional, ~5 %/año sobre capital a 1x) y los 4 lados de coste se comen
  buena parte de los periodos cortos de funding alto.
- Siguiente idea relacionada (no esta hipótesis): carry en altcoins con funding
  persistentemente alto, con universo que incluya pares deslistados.

## Reproducibilidad
`python3 -m src.download && python3 experiments/h001_g1_data.py &&
python3 experiments/h001_carry.py && python3 experiments/h001_g3_walkforward.py`
Hashes de datos: data_manifest.json. Commit de los resultados: ver campo "commit" en los JSON.
