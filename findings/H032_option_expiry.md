# H032 — Vencimiento mensual de opciones de Deribit

**Veredicto: RECHAZADA en G2.** Fecha: 2026-10-13. Variantes: 2 (contador global: 123).

## Tesis (G0)
La cobertura gamma de los dealers crea flujos predecibles alrededor del vencimiento
mensual (último viernes, 08:00 UTC). Ventanas de 48 h antes/después; dirección = signo
de la media en train; perps BTC/ETH; 0,20 % de coste por operación; funding.

## Evidencia (reports/h032.json)
| ventana | periodo | n | media bruta | t bruto | neto/operación | t neto |
|---|---|---|---|---|---|---|
| 48 h antes | train | 72 | +0,19 % | 0,29 | −0,08 % | −0,12 |
| 48 h antes | OOS | 66 | −0,56 % | −1,29 | −0,81 % | −1,88 |
| 48 h después | train | 72 | +0,91 % | 1,56 | +0,63 % | 1,08 |
| 48 h después | OOS | 66 | +0,57 % | 1,90 | +0,32 % | 1,07 |

## Por qué se rechaza
Nada significativo. La ventana posterior (+0,57 % OOS) es similar a la deriva media de
cualquier ventana de 48 h en 2023–2025 (≈ +0,35 % con buy & hold anual de ~64 %), así
que no se distingue del retorno de mercado.

## Reproducibilidad
`python3 experiments/h032_option_expiry.py`.
