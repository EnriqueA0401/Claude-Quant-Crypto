# STATE

## Contador global de pruebas
42  (H001: 6 · H002: 8 · H003: 4 · H007: 6 · H006: 12 · H005: 6)

## Qué se está haciendo
Cerradas (4): H001 rech. G4, H002 rech. G5, H003 rech. G2, H007 rech. G2. Ver findings/.
Universo USDT-M completo descargado (900 símbolos con deslistados, klines 1d + funding).
H006 (corto tras listado) G2 hecho (reports/h006_g2.json): media +2–7 %/evento en las 12
variantes, mediana +8–20 %, pero IC95 por meses incluye 0 en todas. Pasa a G3.
H005 (momentum cross-sectional) G2 ejecutándose (reports/h005_g2.json al terminar).

## Siguiente paso exacto
1. Ejecutar experiments/h006_g3_walkforward.py (selección por t en train, folds de
   6 meses desde 2023, purga 31 días, holdout desde 2025-10 excluido) y decidir.
2. Leer reports/h005_g2.json y decidir si H005 pasa a G3 o se rechaza.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H006 (G3) y H005 (G2).
