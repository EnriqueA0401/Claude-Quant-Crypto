# H014 — Ejecución maker (cota superior)

**Veredicto: RECHAZADA (cota superior negativa).** Fecha: 2026-10-13. Variantes: 4 (contador global: 87).

## Tesis (G0)
Los takers impacientes pagan el spread; ejecutando con órdenes limit, los efectos de
corto plazo que existen en bruto pero no pagan costes taker podrían ser rentables.

## Método
En vez de modelar la cola con aggTrades (caro), se calculó primero una **cota superior**:
todas las órdenes se llenan como maker, sin slippage ni selección adversa, con las
comisiones VIP0 de Binance (perp maker 0,02 %, spot maker 0,10 %: en VIP0 el maker spot
no es más barato que el taker). Si la cota es negativa, ningún modelo realista de cola
puede dar un resultado positivo.

## Evidencia (reports/h014_maker_bound.json; H009 en train 2020–2022)
Coste por entrada con maker perfecto: 0,12 % del capital (frente a 0,25 % taker).
Basis capturado por entrada: 0,035–0,074 %. **Neto por entrada negativo en las 8
combinaciones (−0,002 % a −0,068 %)**; retorno anual −0,07 % a −4,6 %.
Las demás señales de horizonte corto (H003, H004, H007) no eran significativas ni en
bruto (t ≤ 1,8, ninguna supera Bonferroni), así que abaratar la ejecución no las valida.

## Por qué se rechaza
Ni en el caso más optimista la ejecución maker vuelve positivo el único efecto bruto
real (convergencia del basis spot-perp), por la comisión de la pata spot.

## Qué se aprendió
Con capital < 1.000 USD (VIP0), la pata spot cuesta 0,10 % por lado sea maker o taker:
cualquier arbitraje spot-perp necesita > 0,24 % de convergencia por operación.

## Reproducibilidad
`python3 experiments/h014_maker_bound.py`.
