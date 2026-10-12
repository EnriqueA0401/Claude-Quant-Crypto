# STATE

## Contador global de pruebas
67  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (14, todas rechazadas): H001–H013. La mejor: H012 (basis trimestral BTC/ETH:
OOS 3,6 %/año, Sharpe 1,7) rechazada en G4 (no generaliza a altcoins; 24 ops).
Pendiente: H014 (ejecución maker). Meta-review 1 en reports/meta_review.md.
Reglas: Sharpe mensual; alfa vs B&H y nulo aleatorio; variantes registradas antes de
ejecutar; tests 1–3 por experimento; liquidaciones pesimistas; desempates deterministas.

## Siguiente paso exacto
1. Generar nuevas hipótesis (≥ 4) con G0 escrito, priorizando lo que la meta-review
   marca como no agotado: ejecución maker (H014), efectos de baja rotación, mercados/
   periodos con menos eficiencia (listados spot nuevos, pares pequeños), eventos.
2. H014: descargar aggTrades de 1–2 meses de BTCUSDT perp para modelar fills maker.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna (siguiente: nuevas hipótesis + H014).
