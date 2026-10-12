# HYPOTHESES

Estados: pendiente / en curso / rechazada / validada. Gate = último gate superado.
Prioridad = probabilidad a priori / coste de probarla (A alta, B media, C baja).

| id | fuente | racional (resumen) | estado | gate | motivo | variantes | prio |
|----|--------|--------------------|--------|------|--------|-----------|------|
| H001 | anomalía conocida (carry) | cash-and-carry: largo spot + corto perp cobra funding | pendiente | - | - | 0 | A |
| H002 | Liu & Tsyvinski (2021) | momentum de series temporales en BTC/ETH | pendiente | - | - | 0 | A |
| H003 | propia / crowding | funding extremo predice retorno negativo del perp | pendiente | - | - | 0 | A |
| H004 | microestructura | reversión tras cascadas de liquidación (caída + OI cae) | pendiente | - | - | 0 | B |
| H005 | Liu, Tsyvinski & Wu (2022) | momentum cross-sectional semanal entre perps líquidos | pendiente | - | - | 0 | B |
| H006 | eventos de listado | nuevos perps caen tras su listado | pendiente | - | - | 0 | B |
| H007 | estacionalidad intradía | retornos por hora del día / alrededor del funding | pendiente | - | - | 0 | C |

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

### H003 — Funding extremo → retorno negativo
- Quién pierde: largos sobre-apalancados que pagan funding alto y son liquidados.
- Predicción falsable: cuando el funding está en el decil superior (calculado solo con
  datos pasados), el retorno del perp en las siguientes 24–72 h es negativo y un corto
  neto de costes y funding cobrado tiene media > 0.

### H004 — Reversión tras liquidaciones
- Quién pierde: liquidados forzosos que venden sin importar el precio.
- Predicción falsable: tras caídas de ≥k desviaciones típicas en 1 h con caída de OI,
  el retorno de las siguientes 4–24 h es positivo neto de costes.

### H005 — Momentum cross-sectional
- Quién pierde: igual que H002, entre activos.
- Predicción falsable: largo top-quintil / corto bottom-quintil por retorno de 1–4
  semanas, universo con pares deslistados; spread neto OOS > 0.
- Riesgo: con <1.000 USD el número de posiciones está limitado por el nocional mínimo.

### H006 — Deriva negativa tras listado de perps
- Quién pierde: compradores minoristas atraídos por el hype del listado.
- Predicción falsable: corto en perps nuevos durante sus primeros N días tiene retorno
  medio neto de costes y funding > 0, con ≥100 eventos.

### H007 — Estacionalidad intradía
- Quién pierde: flujos predecibles (rebalanceos, funding, apertura de sesiones).
- Predicción falsable: ciertas horas tienen retorno medio distinto de 0 con corrección
  por múltiples comparaciones (24 pruebas) y superan costes de ida y vuelta.
- Prior bajo: el efecto típico es menor que 0,30% de coste de ida y vuelta.
