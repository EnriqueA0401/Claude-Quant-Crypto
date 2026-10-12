# H003 — Funding extremo predice retorno negativo del perp

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-12. Variantes: 4 (contador global: 18).

## Tesis (G0)
Los largos sobre-apalancados que pagan funding alto acaban liquidados: tras un funding
en su percentil ≥ p (frente a los últimos 1095 eventos, solo pasado), un corto 1x de
H horas gana neto de costes y cobrando funding. p ∈ {0,90; 0,95} × H ∈ {24, 72}.

## Evidencia (train 2020–2022, BTC y ETH, reports/h003_g2.json)
| variante | ops | media/op | t | nulo aleatorio | p vs nulo |
|---|---|---|---|---|---|
| BTC p=0,90 H=24 | 85 | −0,17 % | −0,30 | −0,30 % | 0,40 |
| BTC p=0,90 H=72 | 41 | −0,70 % | −0,51 | −0,49 % | 0,57 |
| BTC p=0,95 H=24 | 51 | +0,16 % | 0,22 | −0,31 % | 0,20 |
| BTC p=0,95 H=72 | 28 | +0,94 % | 0,56 | −0,47 % | 0,12 |
| ETH (4 variantes) | 29–97 | −0,4 % a −2,1 % | −0,5 a −1,4 | — | 0,49–0,80 |

El nulo son cortos en momentos aleatorios con el mismo número de operaciones y duración
(500 simulaciones); en 2020–2022 los cortos pierden de media por la deriva alcista.

## Por qué se rechaza
Ninguna variante tiene t > 0,6 ni bate al nulo con p < 0,10, ni siquiera in-sample.
Las únicas medias positivas (BTC p=0,95) se basan en 28–51 operaciones con t < 0,6 y el
mismo filtro pierde en ETH. Seguir a G3 sería buscar ruido.

## Qué se aprendió
- Un funding alto en BTC/ETH no anticipa caídas en 1–3 días: el mercado puede seguir
  subiendo con funding alto (regímenes alcistas de 2020–2021).
- Bug evitado antes de ejecutar: con funding fijo en 0,01 % los empates daban percentil
  1,0 y disparaban constantemente; el rango debe ser estricto.

## Reproducibilidad
`python3 experiments/h003_funding_extreme.py`. Señal en src/signals.py
(funding_extreme_short) con tests de timing, anti-lookahead y no solapamiento.
