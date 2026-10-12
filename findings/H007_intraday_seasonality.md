# H007 — Estacionalidad intradía por bloques de 4 h

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-12. Variantes: 6 (contador global: 24).

## Tesis (G0)
Flujos predecibles (sesiones, funding, rebalanceos) crean retornos medios distintos de 0
en ciertos bloques horarios UTC. Operar el bloque en la dirección del signo, 1x, perps.

## Evidencia (train 2020–2022, BTC+ETH, 1.096 días, reports/h007_g2.json)
| bloque UTC | media bruta | t | p | neto por operación |
|---|---|---|---|---|
| 00–04 | −0,069 % | −1,33 | 0,18 | −0,131 % |
| 04–08 | +0,067 % | 1,54 | 0,12 | −0,151 % |
| 08–12 | +0,017 % | 0,33 | 0,74 | −0,183 % |
| 12–16 | +0,102 % | 1,78 | 0,07 | −0,116 % |
| 16–20 | +0,023 % | 0,47 | 0,64 | −0,177 % |
| 20–24 | +0,097 % | 1,80 | 0,07 | −0,121 % |

## Por qué se rechaza
Ningún bloque es significativo con Bonferroni (α = 0,0083) y ninguno cubre el coste de
ida y vuelta de 0,20 % más funding: todos tienen neto negativo incluso in-sample y
eligiendo el signo a posteriori (lo que ya es optimista).

## Qué se aprendió
Con costes taker de 0,10 % por lado, cualquier efecto intradía debe superar ~0,2 % por
operación; los efectos de calendario en BTC/ETH son 5–10 veces menores. Solo tendría
sentido con órdenes maker y modelando la cola (no asumido aquí).

## Reproducibilidad
`python3 experiments/h007_intraday.py`.
