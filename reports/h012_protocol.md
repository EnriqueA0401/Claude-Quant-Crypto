# H012 — Protocolo de revisión

## Paso 4: doble implementación (2026-10-13)
Reimplementación independiente por eventos: experiments/h012_independent.py →
reports/h012_independent.json (BTC y ETH, contratos que vencen antes de 2023-01-01).
- 7 de 8 combinaciones (activo × variante) coinciden exactamente (PnL, entradas, costes).
- BTC θ = 10 %: 0,0773 (nuestro) frente a 0,0851 (independiente), mismas entradas y costes.
  Causa explicada al 100 %: 10 horas de mantenimiento del spot con posición abierta. La
  versión independiente rellenaba el spot con el último precio (retorno 0) mientras el
  futuro seguía moviéndose, lo que crea basis ficticio; la nuestra mide ambas patas en
  los mismos instantes. Es la correcta y además la más pesimista. Paso 4: superado.
