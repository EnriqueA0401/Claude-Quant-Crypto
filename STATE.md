# STATE

## Contador global de pruebas
101  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (25 rechazadas). Activa: H022 (reabierta por excepción). H025 rechazada (dossier). La más cercana a una ventaja: H022 (carry trimestral
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
1. H022 · paso 6 (red team): subagente con instrucción de REFUTARLA; responder por
   escrito a cada objeción en reports/dossiers/DOSSIER_H022_cm_carry.md.
2. H022 · G5: DSR con el contador global, PBO (CSCV sobre θ ∈ {3,5,7 %} × salida),
   SPA/White si procede, bootstrap por bloques del retorno neto.
3. H022 · G6: tamaño de contrato (100 USD BTC, 10 USD ETH) con < 1.000 USD.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H022 (excepción de G4 por número de operaciones).
