# H019 — Funding negativo sostenido (cortos concurridos) → largo

**Veredicto: RECHAZADA en G3.** Fecha: 2026-10-13. Variantes: 4 (contador global: 83).

## Tesis (G0)
Los cortos apalancados que pagan funding acaban cerrando en un squeeze. Evento: inicio de
un episodio de 3 días con funding medio (equivalente 8 h) < u; largo 1x N días.
Universo top 30 por volumen (380 símbolos con deslistados). u ∈ {0; −0,0001} × N ∈ {7, 14}.

## Evidencia (reports/h019.json)
| variante | train: eventos, media, t, p vs nulo | OOS 2023–25: eventos, media, t, p vs nulo |
|---|---|---|
| u 0, N 7 | 911, +2,42 %, 3,46, 0,00 | 820, +0,74 %, 1,28, 0,37 |
| u 0, N 14 | 714, +3,07 %, 2,85, 0,12 | 647, +2,63 %, 2,84, 0,10 |
| **u −1e-4, N 7 (elegida: mayor t en train)** | 677, +2,84 %, **3,97**, 0,00 | **445, −0,39 %, −0,47, 0,73** |
| u −1e-4, N 14 | 536, +4,24 %, 3,06, 0,03 | 365, +0,24 %, 0,20, 0,64 |

## Por qué se rechaza
La regla de selección fijada de antemano (mayor t en train) elige una variante que es
negativa OOS. La variante u = 0, N = 14 es positiva OOS (t = 2,84), pero elegirla ahora
sería seleccionar mirando el periodo de test (prohibido) y además no bate al nulo de
fechas aleatorias con claridad (p = 0,10): en 2023–2025 comprar altcoins en fechas al
azar también ganaba.

## Qué se aprendió
- La señal in-sample más fuerte hasta ahora (t ≈ 4 frente al nulo) se desvanece OOS:
  sexto caso del patrón "2020–2022 engaña".
- Queda como observación para una hipótesis futura independiente: el efecto "funding
  negativo → rebote" a 14 días, que habría que probar con un periodo nuevo (holdout
  2025-10 → 2026-09) y no con el ya visto.

## Reproducibilidad
`python3 experiments/h019_negative_funding.py`. Test en tests/test_h005_h006.py.
