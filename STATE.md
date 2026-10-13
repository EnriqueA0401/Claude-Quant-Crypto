# STATE

## Contador global de pruebas
111  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (28, todas rechazadas). H022 rechazada en G5 tras la excepción y el red team.
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
1. Meta-review 3 al cerrar la 30.ª (faltan 2). Skew histórico de Deribit no es gratuito;
   MVRV (H027) rechazada. Siguientes ideas: (a) basis COIN-M vs USDT-M (diferencia entre
   trimestrales de la misma moneda, delta-neutral); (b) funding de BTC vs ETH (spread de
   funding, neutral); (c) volatilidad realizada vs implícita para vender gamma vía perps
   no es posible sin opciones → descartar.
   Fijar variantes antes de ejecutar; comparar siempre con buy & hold y con caja.
2. El holdout 2025-10 → 2026-09 sigue intacto.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
