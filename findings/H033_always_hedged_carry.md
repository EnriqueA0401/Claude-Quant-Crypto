# H033 — Carry COIN-M BTC/ETH siempre cubierto (solo se rota el futuro)

**Veredicto: RECHAZADA en el holdout.** Fecha: 2026-10-13. Variantes: 1 (contador global: 139).

## Tesis y diseño (fijados antes de ver resultados)
Mantener BTC/ETH (50/50) como margen y estar siempre corto en el trimestral COIN-M más
cercano con ≥ 14 días, rotando al vencimiento; costes de futuro 0,10 % por lado por
rotación; spot 0,15 % por lado solo al inicio y al final. Origen: objeción 9 del red team
de H022 (dossier H022 §12).

## Evidencia
| periodo | %/año | Sharpe m. | MDD | exceso vs caja 4,5 % |
|---|---|---|---|---|
| 2021–2022 (train) | 5,74 % | 1,65 | −7,2 % | +1,2 % |
| 2023-01 → 2025-09 (contaminado: visto por H012/H022) | 7,57 % | 1,72 | −2,5 % | +3,1 % (IC95 [−0,2 %, +7,2 %]) |
| **holdout 2025-10 → 2026-09 (una sola vez)** | **2,08 %** | **2,46** | **−0,7 %** | **−2,4 %** |

## Por qué se rechaza
En el único periodo limpio, el carry rindió 2,1 %/año, por debajo del rendimiento de la
caja (criterio fijado: > 4,5 %). El Sharpe alto refleja solo la volatilidad casi nula,
no una ventaja. El exceso de 2023–2025 dependía del régimen alcista apalancado de 2024;
con el basis comprimido (2025–26) el carry rinde menos que el efectivo.

## Consecuencia
El holdout queda consumido (registrado antes de ejecutarlo en HYPOTHESES.md y STATE.md).
Con esto se cierra la familia carry: rinde aproximadamente el tipo libre de riesgo, a
veces más (2024) y a veces menos (2023, 2025–26), sin ventaja explotable.

## Reproducibilidad
`python3 experiments/h033_always_hedged.py` (informativo) y `... holdout`
(reports/h033_holdout.json).
