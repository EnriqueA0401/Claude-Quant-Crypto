# Meta-review 1 (10 hipótesis cerradas) — 2026-10-13

Contador global: 55 pruebas. Validadas: 0. Rechazadas: 10.

| familia | hipótesis | resultado |
|---|---|---|
| Carry / funding | H001 (BTC/ETH), H008 (XS), H011 (altcoins cubierto) | funding real, pero neto ≤ 0 o < stablecoins |
| Momentum / tendencia | H002 (TS), H005 (XS), H010 (volumen) | in-sample bueno 2020–21, OOS no significativo |
| Reversión / eventos | H003 (funding extremo), H004 (liquidaciones), H006 (listados) | sin señal o mediana sin media |
| Calendario | H007 (intradía) | efecto 5–10× menor que el coste |

## ¿Qué familias están agotadas?
- **Momentum direccional (TS y XS) y señales derivadas (volumen):** agotadas con datos
  diarios/semanales y ejecución taker. Funcionan en 2020–2021 y no después.
- **Señales intradía con órdenes taker:** agotadas. Ida y vuelta ≥ 0,20 % (perps) y
  ≥ 0,30–0,50 % (spot/altcoins) supera cualquier efecto horario medido.
- **Eventos de capitulación/listado:** sin media positiva tras costes.

## Patrones
1. **El periodo de train 2020–2022 engaña.** H002, H005, H008 y H010 dan in-sample
   excelente y se desvanecen en 2023–2025. Por eso G3 sigue siendo imprescindible.
2. **Los costes deciden.** Todo efecto de horizonte ≤ 1 semana con 4 lados taker en
   altcoins (0,5 % ida y vuelta) queda por debajo del coste.
3. **El carry existe pero es pequeño o arriesgado.** Sin cobertura, el precio lo anula;
   con cobertura, sobran costes y faltan oportunidades.
4. **Los bugs aparecen en los detalles** (funding 4 h/1 h, empates en 0,01 %, pares
   suspendidos, liquidaciones). Los pasos 4–5 del protocolo merecen su coste.

## ¿Cambiar de enfoque? Sí, en tres direcciones
1. **Carry con rendimiento fijado a la entrada (futuros trimestrales).** Comprar spot y
   vender el trimestral fija el basis hasta el vencimiento: 2 lados por pata por
   trimestre, sin funding variable. Prior medio-alto, coste bajo (datos disponibles
   desde 2021). → H012.
2. **Combinar señales débiles (ML) a horizonte semanal** con walk-forward estricto:
   cada señal sola no paga costes, pero un ranking compuesto podría. Contar cada
   configuración del modelo como prueba. → H013.
3. **Ejecución maker:** la mayor palanca es el coste. Modelar órdenes limit con la cola
   (aggTrades) para estrategias de horizonte corto. Coste alto (datos pesados). → H014.

Prioridad: H012 → H013 → H009 → H014.
