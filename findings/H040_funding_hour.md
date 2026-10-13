# H040 — Deriva en la hora previa a la liquidación del funding (cota bruta)

**Veredicto: RECHAZADA (cota bruta).** Fecha: 2026-10-13. Variantes: 2 (contador global: 136).

## Evidencia (reports/h040.json; BTC, ETH, SOL, BNB, XRP perps 1h, 2020–2022)
Retorno de la hora previa a 08/16/00 UTC con signo contrario al último funding liquidado:
| condición | n | media bruta | t |
|---|---|---|---|
| todo funding ≠ 0 | 14.157 | −0,011 % | −1,07 |
| |funding| ≥ 0,03 % | 3.387 | −0,031 % | −1,16 |
El efecto (no significativo) va incluso a favor del lado que paga. Ni de lejos supera el
coste maker de ida y vuelta (0,04 %). Rechazada sin más pruebas.

## Reproducibilidad
`python3 experiments/h040_funding_hour.py`.
