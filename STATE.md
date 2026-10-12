# STATE

## Contador global de pruebas
61  (… H010 2 · H011 4 · H012 4 · H013 2; detalle en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (10, todas rechazadas). Meta-review 1 escrita (reports/meta_review.md): cambio
de enfoque hacia carry fijado (H012), combinación de señales (H013) y ejecución maker
(H014). Motor semanal corregido tras pasos 4–5.
Reglas: Sharpe mensual; alfa vs B&H y nulo aleatorio; variantes registradas antes de
ejecutar; tests 1–3 por experimento; liquidaciones pesimistas.

## Siguiente paso exacto
1. H012 (basis trimestral): G3 superado (reports/h012_g3.json: OOS 3,6 %/año sobre
   capital, Sharpe 1,73, MDD 2,2 %, IC95 > 0, positiva 2023/24/25) pero solo 24 ops.
   G4: aplicar la variante elegida (θ=5 %, salida anticipada) SIN rediseñar a los
   trimestrales COIN-M de 12 monedas no usadas (data/cm.log) + costes ×2 + vecinos.
2. H013 rechazada en G3 (findings/H013_composite_ranking.md).

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H012 (G4 ejecutándose: experiments/h012_g4_robustness.py).
