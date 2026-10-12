# STATE

## Contador global de pruebas
6  (H001: 6 variantes G2)

## Qué se está haciendo
H001 (cash-and-carry). G1 OK. G2 hecho (reports/h001_g2.json, train 2020–2022):
Sharpe anual 3,6–3,9 con θ≤2e-4 en BTC y ETH, ~7–9%/año, MDD ~1–2%, solo 6–11
entradas. SOSPECHA DE BUG (Sharpe > 3) hasta pasar los pasos 4–5 del protocolo.
Corregido: la liquidación usa mark price (mecha falsa ETH 2020-03-13 a 323).
ALERTA G4: con 6–11 entradas en 3 años no se llegará a 100 operaciones OOS.

## Siguiente paso exacto
1. Pasos 4–5 del protocolo para src/carry.py (subagentes: reimplementación
   independiente + revisión por checklist). Resolver cualquier diferencia > 1%.
2. H001 · G3: walk-forward con purga/embargo en 2020-01→2025-09 eligiendo la variante
   solo con el train de cada fold. Holdout 2025-10→2026-09 intacto.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
