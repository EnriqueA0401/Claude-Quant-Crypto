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

---

# Meta-review 2 (20 hipótesis cerradas) — 2026-10-13

Contador global: 83 pruebas. Validadas: 0. Rechazadas: 20 (H001–H013, H015–H020).

## Resultados nuevos desde la meta-review 1
| hipótesis | gate | resultado clave |
|---|---|---|
| H012 basis trimestral BTC/ETH | G4 | **única positiva OOS** (3,3 %/año, Sharpe 1,6, MDD 1 %), pero < efectivo, 18 ops, no generaliza a 12 altcoins |
| H013 ranking ML compuesto | G3 | ridge 17,7 %/año OOS, IC95 incluye 0 |
| H015 MAX / H016 baja beta | G3 | beta in-sample Sharpe 1,23 → OOS −33 %/año |
| H017 tendencia multi-moneda | G3 | sin alfa frente a BTC |
| H018 purga de OI diaria | G2 | el precio sigue cayendo tras la purga |
| H019 funding negativo | G3 | t = 3,97 in-sample → negativa OOS con la regla fijada |
| H020 ETH/BTC | G2 | negativa |
| H009 basis spot-perp 1h | G2 | convergencia 3–7× menor que el coste |
| H010 volumen | G2 | sin señal |

## ¿Qué familias están agotadas?
- **Todo lo direccional cross-sectional en altcoins** (momentum, reversión, volumen, MAX,
  beta, funding XS, ML compuesto): 7 hipótesis, mismo destino. In-sample 2020–2022 bueno,
  OOS 2023–2025 nulo o invertido. Agotada.
- **Eventos de capitulación y crowding** (liquidaciones 1h, purga de OI diaria, funding
  extremo positivo y negativo, listados): agotada.
- **Arbitrajes de basis con ejecución taker** (spot-perp 1h, cash-and-carry perp): el
  efecto existe pero es menor que 4 lados de costes. Agotada salvo con ejecución maker.
- **Carry fijado (trimestrales):** positivo y limpio en BTC/ETH, pero no supera la caja.

## Patrones
1. **Régimen.** 2020–2022 (bull de altcoins + crash) es un train sesgado. Seis hipótesis
   pasaron G2 con nota y fallaron en G3. G3 está haciendo su trabajo: ningún falso
   positivo ha llegado a G5.
2. **El techo es el coste**, no la señal: todos los efectos de microestructura medidos
   (basis, intradía) son positivos brutos pero menores que 0,2–0,5 % por ida y vuelta.
3. **La única "ventaja" estable es carry de bajo riesgo**, cuyo rendimiento (3–4 %/año
   sobre capital en 2023–25) no compensa frente a un depósito en USDT (≈ 4–5 %).
4. Los pasos 4–5 del protocolo encontraron errores relevantes en 4 de 5 motores
   (empates, funding 4 h/1 h, contratos vencidos, liquidaciones). Mantenerlos siempre.

## ¿Cambiar de enfoque? Sí
1. **Prioridad 1 — reducir costes de verdad (H014):** el único camino para los efectos
   que sí existen (basis spot-perp, carry) es ejecución maker. Requiere modelar fills con
   aggTrades (fill solo si el precio cruza). Coste alto, pero es la palanca dominante.
2. **Prioridad 2 — carry combinado de bajo riesgo:** H012 (trimestral) + H001 (perp) en
   BTC/ETH como una sola cartera de "cash-plus", juzgada contra el rendimiento de USDT.
   Si no supera la caja neta de costes, cerrar la familia definitivamente.
3. **Prioridad 3 — señales con periodo nuevo:** cualquier observación surgida al mirar
   OOS (p. ej. H019 u = 0, N = 14) solo puede probarse en el holdout 2025-10 → 2026-09,
   una única vez, y contando la prueba. Reservar el holdout para la mejor candidata.
4. **No más** hipótesis direccionales cross-sectional de altcoins sin un mecanismo nuevo.
