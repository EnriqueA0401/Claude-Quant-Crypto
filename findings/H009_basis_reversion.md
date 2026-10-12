# H009 — Reversión del basis spot-perp extremo

**Veredicto: RECHAZADA en G2 (in-sample).** Fecha: 2026-10-13. Variantes: 4 (contador global: 65).

## Tesis (G0)
Traders impacientes empujan el perp por encima del spot; una cobertura (largo spot +
corto perp) gana cuando el basis converge. Entrada si el basis 1h está en su percentil
≥ p de 720 h; salida al volver a la mediana o tras H horas. p ∈ {0,99; 0,995} × H ∈ {8, 24}.

## Evidencia (train 2020–2022, BTC y ETH; reports/h009_g2.json)
| variante | entradas BTC/ETH | basis capturado/entrada | coste/entrada | neto/entrada |
|---|---|---|---|---|
| p=0,99 H=8 | 201 / 219 | 0,035 % / 0,052 % | 0,25 % | −0,20 % / −0,18 % |
| p=0,99 H=24 | 148 / 168 | 0,046 % / 0,065 % | 0,25 % | −0,17 % / −0,15 % |
| p=0,995 H=8 | 122 / 127 | 0,041 % / 0,059 % | 0,25 % | −0,19 % / −0,17 % |
| p=0,995 H=24 | 100 / 103 | 0,055 % / 0,074 % | 0,25 % | −0,16 % / −0,13 % |
Retorno anual: −4,5 % a −13 % en todas.

## Por qué se rechaza
La convergencia existe (basis capturado > 0 en todas las variantes) pero es 3–7 veces
menor que el coste de 4 lados (0,25 % del capital por ida y vuelta).

## Qué se aprendió
El basis spot-perp de BTC/ETH en 1h es demasiado estrecho para un arbitraje taker. Solo
sería viable con órdenes maker en ambas patas (H014) o en pares con basis mucho mayor.

## Reproducibilidad
`python3 experiments/h009_basis.py`. Test de señal en tests/test_signals.py.
