# STATE

## Contador global de pruebas
93  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (23, todas rechazadas). La más cercana a una ventaja: H022 (carry trimestral
COIN-M BTC/ETH, moneda como margen): OOS 6,4 %/año, Sharpe 1,35, MDD 2,6 %, 3 años
positivos; falla G4 (31 ops < 100, altcoins negativas, costes ×2 < USDT).
DECISIÓN PENDIENTE DE LA PERSONA: el mínimo de 100 ops de G4 es inalcanzable para
carry trimestral (ver findings/H022_cm_carry.md). No se cambia sin su permiso.
Manifest de datos: data_manifest.json (resumen) + data_manifest_files.json.gz.
Reglas: comparar con caja (≈ 4–5 %/año); Sharpe mensual; alfa vs B&H y nulo aleatorio;
variantes registradas antes de ejecutar; tests 1–3; liquidaciones pesimistas;
desempates deterministas; validar vencimientos y barras sin operaciones (G1).

## Siguiente paso exacto
1. Nuevas fuentes de hipótesis fuera de lo agotado (meta-review 2): datos externos no
   disponibles en data.binance.vision (opciones Deribit, on-chain) requieren acceso de
   red; comprobar si los hosts responden (deribit.com, api.glassnode, etc.).
2. Mientras tanto: hipótesis de baja rotación en BTC/ETH con funding/basis como filtro
   de riesgo (BIS WP 1087: basis alto predice caídas) juzgada contra buy & hold.

## Bloqueos
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
