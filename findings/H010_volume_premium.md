# H010 — Prima de alto volumen (cross-sectional semanal)

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-13. Variantes: 2 (contador global: 55).

## Tesis (G0)
Un shock de volumen aumenta la visibilidad del activo y precede a subidas (Gervais,
Kaniel y Mingelgrin 2001). Largo los 5 perps (top 50) con mayor volumen semanal relativo
a su media de B semanas, corto los 5 menores. B ∈ {4, 12}. Motor de H005 (corregido).

## Evidencia (train 2020-04 → 2022-12; reports/h010_g2.json)
| B | %/año | Sharpe m. | MDD | IC95 semanal | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|---|
| 4 | 24,9 % | 0,46 | −40 % | [−0,45 %, +1,41 %] | +61 % | +16 % | −10 % |
| 12 | 17,5 % | 0,34 | −49 % | [−0,70 %, +1,34 %] | +59 % | +10 % | −22 % |

## Por qué se rechaza
Ni siquiera in-sample el IC95 excluye el 0; el beneficio se concentra en 2020 y 2022 es
negativo. Con drawdowns del 40–49 % no tiene sentido llevarla a G3.

## Qué se aprendió
El efecto volumen en altcoins parece una variante más del momentum de 2020–2021 (los
pares con más volumen eran los que subían), sin contenido propio.

## Reproducibilidad
`python3 experiments/h010_volume.py` (G3 con `g3`, no ejecutado). Test anti-lookahead en
tests/test_h005_h006.py.
