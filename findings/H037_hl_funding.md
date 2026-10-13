# H037 — Divergencia de funding Hyperliquid vs Binance (señal contraria)

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 130).

## Tesis (G0)
Cuando el funding de Hyperliquid se separa anormalmente del de Binance (|z| > k sobre
90 días), apostar contra el lado concentrado en Hyperliquid en el perp de Binance al día
siguiente. k ∈ {1,5; 2}; BTC/ETH; costes 0,10 % por lado; funding.

## Evidencia (reports/h037.json)
| k | periodo | %/año | Sharpe m. | MDD | días activa |
|---|---|---|---|---|---|
| 1,5 | 2023-05 → 2024-06 | −0,2 % | −0,04 | −10,4 % | 9 % |
| 2 | 2023-05 → 2024-06 | +0,8 % | 0,24 | −8,6 % | 5 % |
| 1,5 | 2024-07 → 2025-09 | −19,7 % | −1,07 | −35 % | 12 % |
| 2 | 2024-07 → 2025-09 | −18,1 % | −1,43 | −27 % | 7 % |

## Por qué se rechaza
Sin señal in-sample y pérdidas grandes OOS: cuando Hyperliquid paga más funding, el
precio tiende a seguir en esa dirección (no a revertir).

## Reproducibilidad
`python3 experiments/h037_hl_funding.py` (funding de Hyperliquid con hash).
