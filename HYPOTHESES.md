# HYPOTHESES

Estados: pendiente / en curso / rechazada / validada. Gate = último gate superado.
Prioridad = probabilidad a priori / coste de probarla (A alta, B media, C baja).

| id | fuente | racional (resumen) | estado | gate | motivo | variantes | prio |
|----|--------|--------------------|--------|------|--------|-----------|------|
| H001 | anomalía conocida (carry) | cash-and-carry: largo spot + corto perp cobra funding | rechazada | G3 | G4: 13 entradas OOS (<100), 1,4 %/año, solo un régimen, falla en BNB | 6 | A |
| H002 | Liu & Tsyvinski (2021) | momentum de series temporales en BTC/ETH | rechazada | G4 | G5: DSR 0,92, PBO 0,54, IC95 incluye 0; alfa vs B&H no significativo | 8 | A |
| H003 | propia / crowding | funding extremo predice retorno negativo del perp | rechazada | G1 | G2: ninguna variante bate al nulo (t<0,6), ETH negativa | 4 | A |
| H004 | microestructura | reversión tras cascadas de liquidación (caída + OI cae) | pendiente | - | - | 0 | B |
| H005 | Liu, Tsyvinski & Wu (2022) | momentum cross-sectional semanal entre perps líquidos | pendiente | - | - | 0 | B |
| H006 | eventos de listado | nuevos perps caen tras su listado | pendiente | - | - | 0 | B |
| H007 | estacionalidad intradía | retornos por hora del día / alrededor del funding | rechazada | G1 | G2: ningún bloque significativo; todos netos < 0 | 6 | C |

## Detalle G0 (escrito ANTES de ver datos)

### H001 — Cash-and-carry spot/perp
- Quién pierde: largos apalancados en perps que pagan funding para mantener exposición.
- Predicción falsable: con entrada solo si el funding medio de las últimas 3 liquidaciones
  > umbral, el funding cobrado supera los costes de 4 lados (spot 0,15% + perp 0,10% por
  lado incl. slippage) con IC95% bootstrap > 0, en BTC, ETH y ≥2 pares no usados al diseñar.
- Riesgos: capital partido en dos patas (<500 USD cada una), margen del corto, mínimos
  de nocional de perps, basis en entrada/salida.

### H002 — Momentum de series temporales (BTC, ETH)
- Quién pierde: inversores que infrarreaccionan y compradores tardíos por herding.
- Predicción falsable: posición = signo del retorno de L días (L∈{7..56}) en perps, con
  rebalanceo diario; Sharpe neto OOS > 0 y DSR > 0,95 con el contador global.
- Variantes fijadas (2026-10-12, antes de ver resultados): L ∈ {7, 14, 28, 56} ×
  {largo/corto, largo/plano} = 8. Perps 1x, barras diarias UTC, funding real.

### H003 — Funding extremo → retorno negativo
- Quién pierde: largos sobre-apalancados que pagan funding alto y son liquidados.
- Predicción falsable: cuando el funding está en el decil superior (calculado solo con
  datos pasados), el retorno del perp en las siguientes 24–72 h es negativo y un corto
  neto de costes y funding cobrado tiene media > 0.
- Variantes fijadas (2026-10-12, antes de ver resultados): en cada liquidación de
  funding, percentil de la tasa frente a los últimos 1095 eventos (mín. 270, solo
  pasado e incluido el actual). Si percentil ≥ p y tasa > 0 → corto 1x en el open
  siguiente durante H horas; sin solapamiento. p ∈ {0,90; 0,95} × H ∈ {24, 72} = 4.
  Referencia nula: cortos en momentos aleatorios con la misma duración.

### H004 — Reversión tras liquidaciones
- Quién pierde: liquidados forzosos que venden sin importar el precio.
- Predicción falsable: tras caídas de ≥k desviaciones típicas en 1 h con caída de OI,
  el retorno de las siguientes 4–24 h es positivo neto de costes.

### H005 — Momentum cross-sectional
- Quién pierde: igual que H002, entre activos.
- Predicción falsable: largo top-quintil / corto bottom-quintil por retorno de 1–4
  semanas, universo con pares deslistados; spread neto OOS > 0.
- Riesgo: con <1.000 USD el número de posiciones está limitado por el nocional mínimo.
- Variantes fijadas (2026-10-12, antes de ver resultados): universo semanal = perps
  USDT-M (incluidos deslistados) con ≥ 90 días de historia y en el top 50 por volumen
  en USDT de los 30 días previos (solo pasado). Rebalanceo los lunes 00:00 UTC.
  Ordenar por retorno de las últimas L semanas, L ∈ {1, 2, 4}; dirección ∈ {momentum,
  reversión} → 6 variantes. 5 largos + 5 cortos, igual peso, 0,5 de capital por lado.
  Costes 0,05 % comisión + 0,10 % slippage por lado; funding real. Train 2020–2022.

### H006 — Deriva negativa tras listado de perps
- Quién pierde: compradores minoristas atraídos por el hype del listado.
- Predicción falsable: corto en perps nuevos durante sus primeros N días tiene retorno
  medio neto de costes y funding > 0, con ≥100 eventos.
- Variantes fijadas (2026-10-12, antes de ver resultados): evento = primer día de
  klines 1d del perp USDT-M (universo completo con deslistados, listados ≥ 2020-01).
  Corto 1x desde el open del día E después del listado (E ∈ {1, 2}) durante N días
  (N ∈ {7, 14, 30}) → 6 variantes. Costes: comisión 0,05 % + slippage 0,15 % por lado
  (poca liquidez inicial). Funding real. Liquidación si el high diario alcanza 2× la
  entrada (pierde el 100 %). Train = listados 2020-01 → 2022-12. Métrica: media neta
  por evento con bootstrap por mes de listado; control: mismo corto menos el de BTC.

### H007 — Estacionalidad intradía
- Quién pierde: flujos predecibles (rebalanceos, funding, apertura de sesiones).
- Predicción falsable: ciertas horas tienen retorno medio distinto de 0 con corrección
  por múltiples comparaciones (24 pruebas) y superan costes de ida y vuelta.
- Prior bajo: el efecto típico es menor que 0,30% de coste de ida y vuelta.
- Variantes fijadas (2026-10-12, antes de ver resultados): 6 bloques de 4 h UTC
  (00–04, …, 20–24). Para cada bloque: retorno medio open-to-open del perp en el bloque
  (BTC+ETH, train 2020–2022), t con errores por bloques de días. Operación: entrar al
  inicio del bloque en la dirección del signo y salir al final; coste de ida y vuelta
  0,20 % + funding. Éxito in-sample: neto > 0 con p < 0,05/6 (Bonferroni).
