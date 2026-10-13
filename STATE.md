# STATE

## Contador global de pruebas
148  (detalle por hipótesis en HYPOTHESES.md)

## Qué se está haciendo
Cerradas (43, todas rechazadas; H035 bloqueada). Mejor XS: H043 (flujo taker), rechazada en G5. H033 rechazada en el holdout (2,1 %/año < caja). Meta-review 3 escrita (reports/meta_review.md). H022 rechazada en G5 tras la excepción y el red team.
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

## Holdout
Política (persona, 2026-10-13): una vez POR HIPÓTESIS, pre-registrado. Usos: H033 (✗ 2,1 %/año),
H043 (cont_7d: +101 %/año, Sharpe 1,32, MDD −50 %, IC95 semanal incluye 0).

## Siguiente paso exacto
1. H043 REABIERTA (en curso): permutación p_familia 0,0045 y holdout pasan el criterio
   pre-registrado, PERO el holdout depende de 3 semanas (pumps de memecoins: PIPPIN +443 %,
   SIREN +292 %, RIVER +197 %); sin top-3 = −6 %/año; mediana semanal −0,3 %; funding
   +66 %/año del bruto 112 %. Pendiente: protocolo pasos 4 (reimplementación independiente)
   y 6 (red team) — los subagentes fallaron por límite de cuota; relanzar. Luego responder
   objeciones; si sobrevive → G6 (DD, capacidad, fills en memecoins) y G7 paper trading
   con datos posteriores a 2026-09 (data.binance.vision diario).
2. Familia carry cerrada (H001, H012, H021, H022, H033, H042).

## Bloqueos
- H035: calendarios de desbloqueo point-in-time no accesibles (DefiLlama de pago; repo
  DefiLlama/emissions-adapters sin acceso desde esta sesión).
- data.binance.vision y data-api.binance.vision: OK (acceso verificado 2026-10-12).
- api.binance.com y fapi.binance.com: HTTP 451 (restricción geográfica). Afecta a
  verificar comisiones en vivo (se usa el supuesto de CLAUDE.md) y a G7 en perps.

## Hipótesis activa
H043 (validación complementaria; scripts experiments/h043_validation.py).
