# H022 — Carry trimestral COIN-M BTC/ETH con la moneda como margen

**Veredicto: RECHAZADA en G4.** Fecha: 2026-10-13. Variantes: 1 + 4 pruebas G4 (contador global: 93).
**Es la hipótesis más cercana a una ventaja encontrada hasta ahora.**

## Tesis (G0)
Estructura clásica de cash-and-carry: comprar la moneda y usarla como margen de un corto
en el trimestral inverso COIN-M. El capital entero está cubierto y el corto no se puede
liquidar. Regla fija heredada de H012-G3: entrar si basis anualizado > 5 %, salir al
vencimiento o si cae bajo 1,25 %. Datos limpios (vencimiento programado, barras sin
operaciones excluidas).

## Evidencia
- **OOS 2023-01 → 2025-09 (reports/h022.json): 6,4 %/año sobre capital, Sharpe 1,35,
  MDD −2,6 %, IC95 > 0; 2023 +2,3 %, 2024 +12,3 %, 2025 +2,8 %.** BTC 6,6 %, ETH 6,2 %.
  Invertida el 89–94 % del tiempo; costes ≈ 3,1 %/año. Supera el listón de 5 % (USDT).
  Train 2021–2022: 5,0 %/año.
- G4 (reports/h022_g4.json):
  | prueba | %/año OOS | Sharpe | resultado |
  |---|---|---|---|
  | vecinos θ 3 % / 7 % | 6,1 % / 6,4 % | 1,29 / 1,34 | ✓ meseta |
  | 3 años positivos | +2,3 / +12,3 / +2,8 % | — | ✓ |
  | costes ×2 | 3,3 % (2023 −1,6 %) | 0,63 | ✗ positiva pero < USDT |
  | 12 altcoins COIN-M | −10,8 % | −1,70 | ✗ |
  | operaciones OOS | 31 | — | ✗ (< 100) |

## Por qué se rechaza
Falla tres criterios de G4: no funciona en otros activos (los trimestrales COIN-M de
altcoins son ilíquidos y su basis es ruido), con costes ×2 cae por debajo del
rendimiento de USDT, y solo tiene 31 operaciones OOS.

## Nota para la persona responsable del marco
El mínimo de 100 operaciones OOS de G4 es estructuralmente inalcanzable para una
estrategia de carry trimestral (≈ 4 rotaciones/año por activo; con BTC y ETH, ~8/año).
Cambiar ese criterio es una decisión de la persona dueña de CLAUDE.md, no del
investigador. Aunque se cambiara, seguiría fallando "otros activos" y "costes ×2 frente
a la caja". El exceso sobre USDT es de ~1,5 %/año con costes ×1: pequeño.

## Riesgos no modelados (si se retomara)
Riesgo de contraparte y de exchange; tasa de USDT variable; tamaño mínimo de contrato
COIN-M (100 USD BTC, 10 USD ETH) frente a < 1.000 USD; la aproximación lineal del
contrato inverso (error de segundo orden); rebalanceo de cobertura cuando el precio sube.

## Reproducibilidad
`python3 experiments/h022_cm_carry.py && python3 experiments/h022_g4.py`.

## Actualización 2026-10-13: excepción autorizada
La persona responsable del marco autorizó, solo para H022, eximir el mínimo de 100
operaciones OOS de G4 para poder seguir estudiándola. Los demás criterios se mantienen;
"otros activos" sigue fallando y queda registrado. Estado: reabierta, siguiente paso
red team (paso 6) y G5. Dossier: reports/dossiers/DOSSIER_H022_cm_carry.md.
