# STATE

## Contador global de pruebas
128  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (35, todas rechazadas; H035 bloqueada por datos). EN PAUSA: H033 (mejor candidata; ver dossier H022 §12). Meta-review 3 escrita (reports/meta_review.md). H022 rechazada en G5 tras la excepción y el red team.
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
1. DECISIÓN DE LA PERSONA: ¿gastar el holdout 2025-10 → 2026-09 en H033 (mejor
   candidata)? Comando: `python3 experiments/h033_always_hedged.py holdout` (UNA vez).
2. Cola casi agotada. Ideas restantes de prior bajo con datos accesibles: funding de
   Hyperliquid como señal para perps de Binance (API POST api.hyperliquid.xyz/info);
   prima de Coinbase (Coinbase public candles). H035 (desbloqueos) bloqueada por datos.
3. Meta-review 4 al cerrar la 40.ª.

## Bloqueos
- H035: calendarios de desbloqueo point-in-time no accesibles (DefiLlama de pago; repo
  DefiLlama/emissions-adapters sin acceso desde esta sesión).
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
Ninguna.
