# H018 — Largo tras purga de apalancamiento diaria (OI cae ≥ θ en un día rojo)

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-13. Variantes: 4 (contador global: 77).

## Tesis (G0)
Los vendedores forzosos de una purga de apalancamiento de todo un día dejan precios
bajos; un largo de N días en el open siguiente gana. Universo: top 30 por volumen
(380 símbolos alguna vez, con deslistados), OI de las métricas 5 min de Binance.
θ ∈ {10 %, 15 %} × N ∈ {7, 28}; costes 0,15 % por lado; funding real.

## Evidencia (reports/h018.json)
| variante | eventos train | media neta | t | nulo (fechas aleatorias) | p vs nulo |
|---|---|---|---|---|---|
| θ 10 %, N 7 | 455 (83 símb.) | −1,94 % | −2,39 | −0,39 % | 0,94 |
| θ 10 %, N 28 | 271 | −3,25 % | −1,74 | +1,22 % | 0,94 |
| θ 15 %, N 7 | 246 | −1,45 % | −1,17 | −0,61 % | 0,71 |
| θ 15 %, N 28 | 183 | −1,15 % | −0,50 | +1,13 % | 0,72 |
Medianas −2,8 % a −7,1 %; aciertos 35–40 %.
Nota de transparencia: el script calculó también 2023–2025 en la misma ejecución
(medias +0,9 % a +1,6 %, p vs nulo ≥ 0,16); no se usó para ninguna decisión y tampoco
muestra señal.

## Por qué se rechaza
In-sample el efecto va en contra: tras una purga diaria de OI el precio sigue cayendo
más que en fechas aleatorias. No hay nada que llevar a G3.

## Qué se aprendió
Coincide con H004 (1 h): la purga de apalancamiento no marca suelo ni a escala horaria
ni diaria en este universo. La evidencia "práctica" (K33) se refería a BTC en fondos
de mercado concretos, no a una regla sistemática.

## Reproducibilidad
`python3 experiments/h018_universe.py && python3 experiments/h018_oi_flush.py`.
Test en tests/test_h005_h006.py.
