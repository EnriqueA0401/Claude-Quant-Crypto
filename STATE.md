# STATE

## Contador global de pruebas
115  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (30, todas rechazadas). Meta-review 3 escrita (reports/meta_review.md). H022 rechazada en G5 tras la excepción y el red team.
Datos externos: Deribit DVOL y Coin Metrics (src/external.py; Coin Metrics NO es point-in-time). La más cercana a una ventaja: H022 (carry trimestral
COIN-M BTC/ETH, moneda como margen): OOS 6,4 %/año, Sharpe 1,35, MDD 2,6 %, 3 años
positivos; falla G4 (31 ops < 100, altcoins negativas, costes ×2 < USDT).
EXCEPCIÓN AUTORIZADA POR LA PERSONA (2026-10-13): solo para H022 se exime el mínimo de
100 ops OOS de G4. El resto de gates se mantiene (G4 otros activos sigue ✗ y se anota).
Dossiers completos: reports/dossiers/DOSSIER_H022_cm_carry.md y DOSSIER_H025_*.md.
Manifest de datos: data_manifest.json (resumen) + data_manifest_files.json.gz.
Reglas: comparar con caja (≈ 4–5 %/año); Sharpe mensual; alfa vs B&H y nulo aleatorio;
variantes registradas antes de ejecutar; tests 1–3; liquidaciones pesimistas;
desempates deterministas; validar vencimientos y barras sin operaciones (G1).

## Siguiente paso exacto
1. Según la meta-review 3: priorizar hipótesis con mecanismo nuevo y evidencia posterior
   a 2022. Candidata siguiente: efectos de microestructura de minutos con aggTrades en
   BTC/ETH perp (p. ej. reversión tras grandes órdenes agresivas), acotando primero con
   la cota de costes maker/taker (como H014) antes de descargar datos pesados.
2. El holdout 2025-10 → 2026-09 sigue intacto.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
