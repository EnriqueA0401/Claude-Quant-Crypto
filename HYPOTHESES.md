# HYPOTHESES

Estados: pendiente / en curso / rechazada / validada. Gate = último gate superado.
Prioridad = probabilidad a priori / coste de probarla (A alta, B media, C baja).

| id | fuente | racional (resumen) | estado | gate | motivo | variantes | prio |
|----|--------|--------------------|--------|------|--------|-----------|------|
| H001 | anomalía conocida (carry) | cash-and-carry: largo spot + corto perp cobra funding | rechazada | G3 | G4: 13 entradas OOS (<100), 1,4 %/año, solo un régimen, falla en BNB | 6 | A |
| H002 | Liu & Tsyvinski (2021) | momentum de series temporales en BTC/ETH | rechazada | G4 | G5: DSR 0,92, PBO 0,54, IC95 incluye 0; alfa vs B&H no significativo | 8 | A |
| H003 | propia / crowding | funding extremo predice retorno negativo del perp | rechazada | G1 | G2: ninguna variante bate al nulo (t<0,6), ETH negativa | 4 | A |
| H004 | microestructura | reversión tras cascadas de liquidación (caída + OI cae) | rechazada | G1 | G2: t ≤ 0,24 en BTC, negativa en ETH; no bate al nulo | 4 | B |
| H005 | Liu, Tsyvinski & Wu (2022) | momentum cross-sectional semanal entre perps líquidos | rechazada | G2 | G3: OOS Sharpe 0,36, IC95 incluye 0, solo gana 2025, MDD 57 % | 6 | B |
| H006 | eventos de listado | nuevos perps caen tras su listado | rechazada | G2 | G3: OOS +0,5 %/evento, t=0,25; negativa 2 de 3 años | 12 | B |
| H007 | estacionalidad intradía | retornos por hora del día / alrededor del funding | rechazada | G1 | G2: ningún bloque significativo; todos netos < 0 | 6 | C |
| H008 | carry cross-sectional (Koijen et al. 2018, adaptado) | largo perps con funding más negativo, corto los más positivos | rechazada | G2 | G3 (re-ejecutado): OOS +15,6 %/año, Sharpe 0,33, IC95 incluye 0, MDD 44 % | 3 | A |
| H009 | microestructura / basis | reversión del basis spot-perp extremo (delta-neutral) | rechazada | G1 | G2: basis capturado 0,04–0,07 % < coste 0,25 % | 4 | B |
| H010 | Gervais, Kaniel & Mingelgrin (2001) | prima de alto volumen: shocks de volumen anuncian subidas | rechazada | G1 | G2: Sharpe 0,34–0,46, IC95 incluye 0, 2022 negativo | 2 | B |
| H011 | lección de H001 | cash-and-carry en altcoins con funding persistente alto | rechazada | G2 | G3: OOS −2,6 %/año, 51 entradas, basis > funding | 4 | A |
| H012 | meta-review 1 | basis de futuros trimestrales fijado a la entrada (spot largo + trimestral corto) | rechazada | G3 | G4: −1,0 %/año en 12 altcoins COIN-M, costes ×2 −7 %; 24 ops en BTC/ETH | 6 | A |
| H013 | meta-review 1 | ranking semanal compuesto de señales débiles (ML, walk-forward) | rechazada | G2 | G3: ridge 17,7 %/año, Sharpe 0,43, IC95 incluye 0; ICsign −53 % | 2 | B |
| H014 | meta-review 1 | ejecución maker con modelo de cola (aggTrades) | rechazada | G2 | cota superior (maker perfecto) negativa en H009: coste 0,12 % > basis 0,07 % | 4 | C |
| H015 | Bali, Cakici & Whitelaw (2011); crypto: lottery demand | efecto MAX: los pares con mayor subida diaria máxima del mes rinden menos | rechazada | G2 | G3: 1,5 %/año, Sharpe 0,04, MDD 59 % | 2 | A |
| H016 | Frazzini & Pedersen (2014), BAB / baja volatilidad | largo baja volatilidad, corto alta volatilidad (cross-section mensual) | rechazada | G2 | G3: −33 %/año (beta in-sample 1,23 se invierte) | 2 | A |
| H017 | Zarattini, Pagani & Barbon (2025), SSRN 5209907 | tendencia multi-moneda largo/plano (ensemble Donchian + tamaño por volatilidad) | rechazada | G2 | G3: 4,5 %/año, alfa vs BTC −1,7 % (no significativo) | 2 | B |
| H018 | práctica (K33): purgas de apalancamiento diarias | largo tras caída diaria de OI ≥ θ (universo top 30) | rechazada | G1 | G2: media −1,2 % a −3,3 %, t −0,5 a −2,4, peor que el nulo | 4 | C |
| H019 | propia / crowding de cortos | funding negativo sostenido anuncia squeeze: largo 1–2 semanas | rechazada | G2 | G3: variante elegida (t=3,97 train) da −0,39 %/evento OOS | 4 | B |
| H020 | valor relativo / rotación | reversión del ratio ETH/BTC tras desviaciones extremas (neutral) | rechazada | G1 | G2: −2,6 %/año, 8–11 entradas | 2 | C |
| H021 | meta-review 2 | cartera carry BTC/ETH: trimestral (H012) y, si no, perp (H001) | rechazada | G3 | OOS 3,5 %/año < 5 % (USDT) | 1 | B |
| H022 | estructura clásica coin-margined | carry trimestral COIN-M BTC/ETH con la moneda como margen (capital completo) | rechazada | G4* | *excepción de 100 ops; G5: PBO 0,51, exceso sobre caja no significativo; red team: depende de 2024-T2 y OOS = H012 | 11 | A |
| H023 | Schmeling, Schrimpf & Todorov (BIS WP 1087) | basis trimestral alto predice caídas: largo spot BTC/ETH solo con basis bajo | rechazada | G1 | G2: peor que B&H in-sample; OOS Sharpe 1,28 < 1,41 B&H, alfa −2,4 % | 2 | B |
| H024 | Moreira & Muir (2017), carteras gestionadas por volatilidad | exposición BTC/ETH ∝ 1/varianza (realizada o implícita DVOL) | rechazada | G1 | G2: alfa −22 %/año in-sample; OOS solo más apalancamiento | 2 | B |
| H025 | Bollerslev, Tauchen & Zhou (2009), prima de varianza | VRP alta (DVOL² − RV²) → largo BTC/ETH la semana siguiente | rechazada | G3 | G4: alfa negativo en SOL/BNB/XRP; en BTC/ETH +15,8 %/año no significativo | 4 | C |
| H026 | on-chain (Coin Metrics): flujos a exchanges | entradas netas anómalas a exchanges anuncian ventas: fuera del mercado 7 días | rechazada | G1* | G2: Sharpe = B&H (0,93 vs 0,94; OOS 1,24 vs 1,26); *datos no point-in-time | 2 | C |
| H027 | valoración on-chain (MVRV) | fuera del mercado cuando el MVRV está en su zona de euforia | rechazada | G1* | G2: alfa −41 %/año in-sample; OOS +7,8 % n.s. | 2 | C |
| H028 | microestructura / segmentación de mercados | convergencia COIN-M vs USDT-M del mismo trimestral (neutral) | rechazada | G2 | G3: OOS ≈ 0 %/año (in-sample ~3 %, Sharpe 1,4): ineficiencia cerrada | 2 | B |
| H029 | carry relativo BTC/ETH | cobrar el diferencial de funding BTC vs ETH (neutral) | rechazada | G1 | G2: negativa; inactiva desde 2023 | 2 | C |
| H030 | microestructura (reversión de corto plazo) | reversión tras minutos extremos en BTC/ETH perp (cota bruta) | rechazada | G1 | cota: rebote bruto 0,01–0,05 %, t < 1,9 (≤ coste maker) | 4 | C |
| H031 | propia: cambio de intervalo de funding de Binance | tras acortarse el intervalo de funding, el lado apalancado pierde | rechazada | G1 | train t≈0,5; OOS por outliers (ALPACA +1.805 %); sin top-3 t=0,65 | 2 | B |

## Detalle G0 (escrito ANTES de ver datos)

### H001 — Cash-and-carry spot/perp
- Quién pierde: largos apalancados en perps que pagan funding para mantener exposición.
- Predicción falsable: con entrada solo si el funding medio de las últimas 3 liquidaciones
  > umbral, el funding cobrado supera los costes de 4 lados (spot 0,15% + perp 0,10% por
  lado incl. slippage) con IC95% bootstrap > 0, en BTC, ETH y ≥2 pares no usados al diseñar.
- Riesgos: capital partido en dos patas (<500 USD cada una), margen del corto, mínimos
  de nocional de perps, basis en entrada/salida.

### H002 — Momentum de series temporales (BTC, ETH)
- Quién pierde: inversores que infrarreaccionan y compradores tardíos por herding.
- Predicción falsable: posición = signo del retorno de L días (L∈{7..56}) en perps, con
  rebalanceo diario; Sharpe neto OOS > 0 y DSR > 0,95 con el contador global.
- Variantes fijadas (2026-10-12, antes de ver resultados): L ∈ {7, 14, 28, 56} ×
  {largo/corto, largo/plano} = 8. Perps 1x, barras diarias UTC, funding real.

### H003 — Funding extremo → retorno negativo
- Quién pierde: largos sobre-apalancados que pagan funding alto y son liquidados.
- Predicción falsable: cuando el funding está en el decil superior (calculado solo con
  datos pasados), el retorno del perp en las siguientes 24–72 h es negativo y un corto
  neto de costes y funding cobrado tiene media > 0.
- Variantes fijadas (2026-10-12, antes de ver resultados): en cada liquidación de
  funding, percentil de la tasa frente a los últimos 1095 eventos (mín. 270, solo
  pasado e incluido el actual). Si percentil ≥ p y tasa > 0 → corto 1x en el open
  siguiente durante H horas; sin solapamiento. p ∈ {0,90; 0,95} × H ∈ {24, 72} = 4.
  Referencia nula: cortos en momentos aleatorios con la misma duración.

### H004 — Reversión tras liquidaciones
- Quién pierde: liquidados forzosos que venden sin importar el precio.
- Predicción falsable: tras caídas de ≥k desviaciones típicas en 1 h con caída de OI,
  el retorno de las siguientes 4–24 h es positivo neto de costes.
- Variantes fijadas (2026-10-12, antes de ver resultados): barras 1h del perp. Evento si
  el retorno close-to-close de la hora ≤ −k·σ (σ = desv. típica de retornos 1h de los 30
  días previos, solo pasado) Y el cambio de OI de esa hora (último dato 5 min de la hora
  frente al de la hora anterior) ≤ su percentil 5 de los 30 días previos. Largo 1x en el
  open siguiente durante H horas, sin solapamiento. k ∈ {3, 4} × H ∈ {4, 24} = 4.
  Costes perp 0,10 % por lado + funding. Nulo: largos aleatorios de igual duración.
  Diseño BTC/ETH, train 2020-09 → 2022-12; SOL/BNB/XRP solo para G4.

### H005 — Momentum cross-sectional
- Quién pierde: igual que H002, entre activos.
- Predicción falsable: largo top-quintil / corto bottom-quintil por retorno de 1–4
  semanas, universo con pares deslistados; spread neto OOS > 0.
- Riesgo: con <1.000 USD el número de posiciones está limitado por el nocional mínimo.
- Variantes fijadas (2026-10-12, antes de ver resultados): universo semanal = perps
  USDT-M (incluidos deslistados) con ≥ 90 días de historia y en el top 50 por volumen
  en USDT de los 30 días previos (solo pasado). Rebalanceo los lunes 00:00 UTC.
  Ordenar por retorno de las últimas L semanas, L ∈ {1, 2, 4}; dirección ∈ {momentum,
  reversión} → 6 variantes. 5 largos + 5 cortos, igual peso, 0,5 de capital por lado.
  Costes 0,05 % comisión + 0,10 % slippage por lado; funding real. Train 2020–2022.

### H006 — Deriva negativa tras listado de perps
- Quién pierde: compradores minoristas atraídos por el hype del listado.
- Predicción falsable: corto en perps nuevos durante sus primeros N días tiene retorno
  medio neto de costes y funding > 0, con ≥100 eventos.
- Variantes fijadas (2026-10-12, antes de ver resultados): evento = primer día de
  klines 1d del perp USDT-M (universo completo con deslistados, listados ≥ 2020-01).
  Corto 1x desde el open del día E después del listado (E ∈ {1, 2}) durante N días
  (N ∈ {7, 14, 30}) → 6 variantes. Costes: comisión 0,05 % + slippage 0,15 % por lado
  (poca liquidez inicial). Funding real. Liquidación si el high diario alcanza 2× la
  entrada (pierde el 100 %). Train = listados 2020-01 → 2022-12. Métrica: media neta
  por evento con bootstrap por mes de listado; control: mismo corto menos el de BTC.
- Resultado de las 6 primeras (G2): mediana +8–20 %/evento, media +2–6 %, IC95 por
  meses incluye 0; las liquidaciones (high ≥ 2× entrada) dominan la cola.
- Variantes añadidas (2026-10-12, ANTES de ver su resultado; total 12): E = 2,
  N ∈ {7, 14, 30}, stop-loss del corto si el high diario ≥ entrada·(1+X), X ∈ {0,3; 0,6}.
  Fill del stop: max(nivel, open del día) + slippage 0,15 %. Racional: cortar la cola de
  pumps que liquidan el corto.

### H007 — Estacionalidad intradía
- Quién pierde: flujos predecibles (rebalanceos, funding, apertura de sesiones).
- Predicción falsable: ciertas horas tienen retorno medio distinto de 0 con corrección
  por múltiples comparaciones (24 pruebas) y superan costes de ida y vuelta.
- Prior bajo: el efecto típico es menor que 0,30% de coste de ida y vuelta.
- Variantes fijadas (2026-10-12, antes de ver resultados): 6 bloques de 4 h UTC
  (00–04, …, 20–24). Para cada bloque: retorno medio open-to-open del perp en el bloque
  (BTC+ETH, train 2020–2022), t con errores por bloques de días. Operación: entrar al
  inicio del bloque en la dirección del signo y salir al final; coste de ida y vuelta
  0,20 % + funding. Éxito in-sample: neto > 0 con p < 0,05/6 (Bonferroni).

### H008 — Carry cross-sectional de funding
- Quién pierde: especuladores apalancados que pagan funding alto por estar largos (y
  cortos que pagan funding negativo) en los pares más concurridos.
- Predicción falsable: cartera semanal larga en los 5 perps (top 50 por volumen) con
  funding medio de 7 días más negativo y corta en los 5 más positivos cobra funding
  neto > costes y su retorno de precio no lo anula; Sharpe OOS > 0, IC95 > 0.
- Variantes fijadas (2026-10-12, antes de ver resultados): mismo universo, rebalanceo,
  costes y tamaño que H005 (top 50 por volumen 30 d, ≥ 90 días, lunes 00:00 UTC,
  5 largos + 5 cortos, 0,5 de capital por lado). Orden por funding medio de los eventos
  de los D días previos (ts < lunes 00:00), D ∈ {3, 7, 14} → 3 variantes.
  Largo = funding más bajo; corto = funding más alto. Train 2020–2022.

### H009 — Reversión del basis spot-perp
- Quién pierde: traders impacientes que empujan el perp lejos del spot.
- Predicción falsable: cuando |perp/spot − 1| supera su percentil 99 de 30 días, una
  posición delta-neutral contra el basis gana al converger en < 24 h, neta de 4 lados.
- Variantes fijadas (2026-10-13, antes de ver resultados): barras 1h, basis =
  close perp / close spot − 1. Percentil del basis frente a las 720 horas previas (solo
  pasado, rango estricto). Solo el lado ejecutable sin cortos spot: si percentil ≥ p →
  largo spot + corto perp (src/carry.run_carry, 1x, w = 0,5, costes 4 lados, funding),
  salida cuando el basis ≤ su mediana de 720 h o tras H horas. p ∈ {0,99; 0,995} ×
  H ∈ {8, 24} = 4. Diseño BTC/ETH, train 2020–2022; SOL/BNB/XRP para G4.

### H010 — Prima de alto volumen
- Quién pierde: vendedores que no anticipan la mayor visibilidad del activo.
- Predicción falsable: altcoins (top 50 por volumen) con volumen diario > 3× su media de
  30 días y retorno no extremo rinden más que el resto en los 5–10 días siguientes.
- Variantes fijadas (2026-10-13, antes de ver resultados): versión cross-sectional
  semanal con el motor de H005 (top 50 por volumen 30 d, ≥ 90 días, deslistados,
  lunes 00:00 UTC, 5 largos + 5 cortos, 0,5 por lado, costes 0,15 % por lado, funding).
  Puntuación = volumen en USDT de la última semana (lun–dom) / volumen semanal medio de
  las B semanas anteriores; largo los 5 mayores, corto los 5 menores. B ∈ {4, 12} → 2.

### H011 — Carry en altcoins
- Quién pierde: largos apalancados en altcoins que pagan funding alto durante semanas.
- Predicción falsable: cash-and-carry (largo spot + corto perp) en altcoins con spot en
  Binance y funding medio de 7 días > umbral supera el rendimiento de stablecoins
  (≥ 5 %/año sobre capital) neto de 4 lados de costes, con ≥ 100 entradas OOS.
- Evidencia previa (H008, OOS 2023–2025): la pata de funding de un long/short de altcoins
  cobró ~33 %/año sobre 0,5 de capital por lado; el precio se lo comió. Cubrir el precio
  con spot es la forma directa de aislar ese funding.
- Variantes fijadas (2026-10-12, antes de ver resultados): semanal (lunes 00:00 UTC).
  Universo: top 50 por volumen perp de 30 d con ≥ 90 días de perp y de spot USDT.
  Elegir los 5 con mayor funding medio de los D días previos (ts < lunes), D ∈ {3, 7};
  filtro θ ∈ {ninguno, media > 3e-4 por evento} → 4 variantes. [Corrección 2026-10-12,
  antes de ejecutar G2: "por evento" = equivalente a 8 h (suma de la ventana / (3·D)),
  porque desde 2023 muchos pares liquidan cada 4 h o 1 h.] Por par: largo spot +
  corto perp, 0,1 de capital por pata (1x). Costes por lado: spot 0,10 % + 0,10 %
  slippage; perp 0,05 % + 0,10 %. Funding real. Liquidación del corto si high perp ≥ 2×
  entrada: pata perp −100 %, la pata spot conserva su retorno real. Train 2020–2022.

### H012 — Basis de futuros trimestrales fijado a la entrada
- Quién pierde: largos apalancados que pagan prima por exposición con vencimiento
  (demanda de apalancamiento sin funding variable).
- Predicción falsable: comprar spot y vender el trimestral de BTC/ETH cuando el basis
  anualizado > umbral y mantener hasta vencimiento rinde, neto de 4 lados y de margen,
  más que las stablecoins (≥ 5 %/año sobre el capital desplegado) con riesgo casi nulo.
- Riesgos: liquidación del corto si el precio se dispara (margen), capital dividido,
  nocional mínimo de los trimestrales, pocas operaciones (4 vencimientos/año).
- Variantes fijadas (2026-10-13, antes de ver resultados): barras 1h. En cada hora sin
  posición, contrato = el trimestral más cercano con ≥ 14 días hasta su última barra.
  Basis anualizado = (F_close/S_close − 1)·365/días restantes. Entrada en el open
  siguiente si basis anualizado > θ. Salida: (a) en la última barra del contrato
  (vencimiento) o (b) antes si el basis anualizado < θ/4. θ ∈ {5 %, 10 %} × {a, b} = 4.
  Largo spot + corto trimestral, 0,5 de capital por pata (1x). Costes por lado: spot
  0,10 % + 0,05 %, futuro 0,05 % + 0,05 % (también en la salida a vencimiento).
  Rebalanceo de margen si el futuro sube > 25 % desde la referencia (coste
  w·|mov|·(cs+cp)); liquidación si el high ≥ ref·(2 − 0,005): pata futuro −100 %, spot
  limitado a +100 %. Capital ocioso al 0 %. Train: contratos que vencen ≤ 2022-12;
  BTC y ETH (ambos de diseño: no hay otros trimestrales).

### H013 — Ranking compuesto de señales débiles
- Quién pierde: la suma de los perdedores de cada señal (momentum, funding, volumen, OI).
- Predicción falsable: un modelo lineal o de árboles reentrenado en walk-forward sobre
  señales semanales ya calculadas genera un long/short con IC95 > 0 OOS neto de costes.
- Variantes fijadas (2026-10-13, antes de ver resultados): mismo universo/motor que
  H005 (top 50, ≥ 90 días, lunes, 5+5, costes 0,15 %, funding). Características por
  lunes, en percentil cross-sectional: retorno 1 sem, retorno 4 sem, funding equiv. 8 h
  de 7 días, ratio de volumen 1/4 sem, volatilidad diaria 30 días. Objetivo: percentil
  del retorno de la semana siguiente (open→open, menos funding). Modelos (2 variantes):
  (a) ridge (λ = 1) sobre percentiles; (b) suma de percentiles con el signo de la IC
  media de cada característica en train. Reentreno al inicio de cada fold de 6 meses
  con todo el pasado (embargo 1 semana). G2 = folds dentro de 2021–2022 (train desde
  2020-04); G3 = folds 2023-01 → 2025-09.

### H014 — Ejecución maker
- Quién pierde: los takers impacientes que pagan el spread.
- Predicción falsable: con órdenes limit modeladas con la cola (aggTrades, fill solo si
  el precio cruza), alguna de las señales intradía rechazadas pasa a neto > 0.

### H015 — Efecto MAX (demanda de lotería)
- Quién pierde: minoristas que compran monedas con subidas diarias extremas recientes
  esperando repetir el pump (preferencia por asimetría positiva) y pagan de más.
- Predicción falsable: cartera mensual larga en los 5 perps (top 50) con menor retorno
  diario máximo de los últimos 30 días y corta en los 5 con mayor; neta de costes y
  funding, Sharpe OOS > 0 e IC95 > 0.
- Variantes fijadas (2026-10-13, antes de ver resultados): motor de H005 con rebalanceo
  cada 4 semanas (primer lunes de cada bloque de 4). MAX = máximo retorno close-to-close
  diario en los N días previos al domingo, N ∈ {30}; y MAX5 = media de los 5 mayores →
  2 variantes. Train 2020–2022, G3 2023-01 → 2025-09.

### H016 — Baja volatilidad / betting-against-beta
- Quién pierde: inversores con restricciones de apalancamiento que compran activos de
  alta beta/volatilidad y les exigen menos retorno del que les corresponde.
- Predicción falsable: cartera mensual larga en los 5 perps de menor volatilidad diaria
  de 30 días y corta en los 5 de mayor; neta de costes, Sharpe OOS > 0 e IC95 > 0.
- Variantes fijadas (2026-10-13, antes de ver resultados): mismo motor y rebalanceo
  cada 4 semanas. Riesgo = volatilidad diaria de 30 días o beta frente a BTC de 60 días
  → 2 variantes. Igual peso (sin escalar por volatilidad).

### H017 — Tendencia multi-moneda (ensemble)
- Quién pierde: compradores tardíos y tenedores que no reducen riesgo en las caídas.
- Predicción falsable: cartera largo/plano sobre los 20 perps más líquidos (con
  deslistados), señal = media de rupturas Donchian de varios horizontes, tamaño inverso
  a la volatilidad; alfa frente a buy & hold de BTC > 0 en 2023–2025 (juzgar solo OOS).
- Nota previa: TS momentum en BTC/ETH (H002) ya falló; el alfa publicado puede venir de
  2017 y 2021.
- Variantes fijadas (2026-10-13, antes de ver resultados): universo diario = top 20
  perps USDT-M por volumen de 30 días (con deslistados). Por moneda y lookback
  L ∈ {10, 20, 40, 80, 160} días: estado 1 si el close supera el máximo de los L
  closes previos, 0 si cae bajo el mínimo de los L/2 previos (Donchian con histéresis).
  Señal = media de los 5 estados. Peso = señal · min(1, 0,8 %/σ60 diaria) / 20 (gross ≤ 1,
  solo largos, perps 1x). Decisión al close, ejecución en el open siguiente; costes
  0,15 % por lado sobre |Δpeso|; funding real. Rebalanceo diario o semanal (lunes) → 2
  variantes. Se elige en train (2020–2022) y se juzga en 2023-01 → 2025-09 contra
  buy & hold de BTC (alfa).

### H018 — Purga de apalancamiento diaria
- Quién pierde: vendedores forzosos en una purga de apalancamiento de todo un día.
- Predicción falsable: tras un día con caída de OI > 10 % (y precio a la baja), un
  largo de 1–4 semanas en BTC/ETH (y en el universo con métricas para llegar a ≥ 100
  eventos) bate a largos en fechas aleatorias neto de costes y funding.
- Variantes fijadas (2026-10-13, antes de ver resultados): universo diario = perps
  USDT-M en el top 30 por volumen de 30 días (incluidos deslistados; solo pasado).
  OI diario = último dato 5 min del día UTC. Evento el día d si OI_d/OI_{d−1} − 1 ≤ −θ y
  el retorno del día < 0. Largo 1x desde el open de d+1 durante N días; costes 0,15 %
  por lado; funding real. θ ∈ {10 %, 15 %} × N ∈ {7, 28} = 4. Nulo: mismos símbolos,
  fechas aleatorias, misma duración (1.000 sims). Train = eventos antes de 2023; OOS =
  2023-01 → 2025-09 con la variante de mayor t en train.

### H019 — Funding negativo sostenido (cortos concurridos)
- Quién pierde: cortos apalancados que pagan funding y acaban cerrando en un squeeze.
- Predicción falsable: tras 3 días con funding medio (equivalente 8 h) < umbral, un largo
  de N días en el perp bate a largos en fechas aleatorias, neto de costes; el largo
  además cobra el funding negativo.
- Variantes fijadas (2026-10-13, antes de ver resultados): universo diario top 30 por
  volumen (380 símbolos, deslistados incluidos). Evento el día d si la media de los
  eventos de funding con ts en (d−3 días, d+1 00:00] (equivalente 8 h) < u y la media
  de los 3 días anteriores ≥ u (inicio del episodio). u ∈ {0; −0,0001} × N ∈ {7, 14}
  = 4. Largo 1x desde el open de d+1; sin solapamiento por símbolo; costes 0,15 % por
  lado; funding real. Nulo: fechas aleatorias del mismo símbolo en el universo.
  Train = eventos antes de 2023; OOS = 2023-01 → 2025-09 con la variante de mayor t.

### H020 — Reversión ETH/BTC
- Quién pierde: rotaciones tardías entre BTC y ETH que sobrerreaccionan.
- Predicción falsable: cuando log(ETH/BTC) se aleja > k desviaciones típicas de su media
  de 90 días, la posición neutral contraria (largo el barato, corto el caro, 0,5 por
  pata, perps) gana hasta volver a la media (o 30 días), neta de 4 lados y funding.
- Variantes fijadas (2026-10-13, antes de ver resultados): z con media y desviación de
  los 90 días previos (closes diarios); k ∈ {2; 2,5}; salida en z cruza 0 o a los
  30 días → 2 variantes. Train 2020–2022, OOS 2023-01 → 2025-09.

### H021 — Cartera carry "cash-plus" BTC/ETH
- Quién pierde: demanda de apalancamiento largo (paga basis trimestral y funding).
- Predicción falsable: combinar el basis trimestral (H012) con el carry del perp (H001)
  en las horas en que H012 no está invertido rinde OOS > 5 %/año sobre capital (por
  encima del rendimiento de USDT), con IC95 > 0.
- Diseño fijado (2026-10-13, antes de ver resultados; 1 variante, parámetros ya
  elegidos en G3 de cada hipótesis, sin reoptimizar): por activo (BTC, ETH; 0,5 del
  capital cada uno) H012 con θ = 5 % y salida anticipada (motor corregido); H001 con
  θ = 1e-4, k = 3, señal forzada a 0 mientras H012 tiene posición o entrada pendiente
  (el motor de H001 cobra sus propias entradas y salidas). Periodo OOS 2023-01 → 2025-09.

### H022 — Carry trimestral COIN-M con la moneda como margen
- Quién pierde: igual que H012 (demanda de apalancamiento largo con vencimiento).
- Mecanismo distinto de H012: estructura de capital. Se compra la moneda y se deposita
  como margen de un corto en el trimestral inverso COIN-M por el mismo valor; el
  capital entero está en la cobertura y el corto no puede liquidarse (el margen sube
  con el precio). Rendimiento ≈ basis completo sobre el capital.
- Predicción falsable: OOS 2023-01 → 2025-09 > 5 %/año sobre capital (por encima de
  USDT), IC95 > 0, positiva los 3 años.
- Diseño fijado (2026-10-13, antes de ver resultados; 1 variante, regla ya elegida en
  H012-G3): BTCUSD_/ETHUSD_ trimestrales COIN-M (datos 1h limpios: vencimiento
  programado, barras sin operaciones excluidas), θ = 5 %, salida anticipada a θ/4,
  W = 1 por pata (aproximación lineal en USD), sin liquidación (cobertura en moneda),
  costes spot 0,15 % y futuro 0,10 % por lado. Cartera 50/50 BTC/ETH.
- Aviso de G4: tendrá < 100 operaciones OOS (≈ 4 vencimientos/año por activo).

### H023 — Basis alto como filtro de riesgo
- Quién pierde: largos apalancados que pagan un basis alto justo antes de las caídas
  (el basis alto refleja apalancamiento minorista y escasez de capital de arbitraje).
- Predicción falsable: estar largo en spot BTC/ETH solo cuando el basis trimestral
  anualizado está por debajo de un umbral (y en efectivo al 0 % si no) tiene mayor
  Sharpe y alfa > 0 frente a buy & hold en 2023-01 → 2025-09.
- Variantes fijadas (2026-10-13, antes de ver resultados): basis diario = close del
  trimestral USDT-M más cercano con ≥ 14 días / close spot − 1, anualizado (datos
  limpios). Señal al close del día, ejecución en el open siguiente. Largo si basis
  anualizado < b, b ∈ {10 %, 15 %} → 2. Costes spot 0,15 % por lado. Cartera 50/50
  BTC/ETH. Elegir b en 2021–2022 (Sharpe mensual) y juzgar en 2023–2025.

### H024 — Carteras gestionadas por volatilidad
- Quién pierde: inversores que mantienen exposición constante en periodos de varianza
  alta, cuando el retorno esperado no compensa el riesgo (la varianza persiste más que
  la prima de riesgo).
- Predicción falsable: escalar la exposición semanal a BTC/ETH (perps) por c/σ² mejora
  el Sharpe frente a buy & hold y da alfa > 0 en 2023-01 → 2025-09.
- Variantes fijadas (2026-10-13, antes de ver resultados): σ² = (a) varianza realizada
  de 30 días de retornos diarios log o (b) (DVOL/100)²/365 de Deribit al close del
  domingo → 2. Peso w = min(1,5; c/σ²), c calibrado para que la media de w sea 1 en
  2021-04 → 2022-12 (solo train). Rebalanceo los lunes, costes 0,10 % por lado sobre
  |Δw|, funding real. Cartera 50/50 BTC/ETH. Elegir variante por Sharpe en train.

### H025 — Prima de riesgo de varianza como señal de timing
- Quién pierde: compradores de protección que pagan de más en momentos de miedo; la
  prima alta indica aversión al riesgo que se compensa con retornos futuros.
- Predicción falsable: estar largo (perp 1x) en BTC/ETH solo las semanas en que
  VRP = (DVOL/100)² − RV² anualizada supera su mediana de las 52 semanas previas da
  mayor Sharpe y alfa > 0 frente a buy & hold en 2023–2025.
- Variantes fijadas (2026-10-13, antes de ver resultados): RV de 7 o 30 días (retornos
  diarios log, anualizada) → 2. Decisión al close del domingo, ejecución el lunes;
  costes 0,10 % por lado; funding. 50/50 BTC/ETH. Elegir por Sharpe en 2021-04 → 2022.
- G4 "otros activos" (fijado 2026-10-13 antes de ejecutarlo): la misma señal de BTC
  (VRP con RV 7 d, mediana 52 semanas) aplicada sin cambios a los perps SOL, BNB y XRP
  (cartera a partes iguales), costes 0,15 % por lado, 2023-01 → 2025-09; éxito si el
  alfa frente a su buy & hold es > 0.

### H026 — Entradas netas anómalas a exchanges
- Quién pierde: compradores que absorben la venta de grandes tenedores que mueven
  monedas a exchanges para vender.
- Predicción falsable: estar largo (perp 1x) en BTC/ETH salvo los 7 días siguientes a
  un día con entrada neta a exchanges anómala da mayor Sharpe y alfa > 0 frente a buy &
  hold en 2023-01 → 2025-09.
- Variantes fijadas (2026-10-13, antes de ver resultados): netflow_d = (FlowInExNtv −
  FlowOutExNtv) / SplyExNtv (Coin Metrics, día UTC d, conocido al cierre de d); z con
  media y desviación de los 90 días previos; si z_d > k → plano del open de d+1 durante
  7 días (se renueva si vuelve a dispararse). k ∈ {1,5; 2} → 2. Costes 0,10 % por lado,
  funding real, 50/50 BTC/ETH. Elegir k en 2020–2022 (Sharpe mensual).
- AVISO G1: los flujos de Coin Metrics no son point-in-time (revisados a posteriori);
  cualquier resultado positivo debe considerarse optimista y no podría validarse sin
  datos en tiempo real (G7).

### H027 — MVRV: evitar la euforia
- Quién pierde: compradores tardíos en fases de euforia, cuando el precio está muy por
  encima del coste medio de adquisición on-chain (realized cap) y los tenedores con
  grandes plusvalías venden.
- Predicción falsable: estar largo en spot BTC/ETH salvo cuando el MVRV supera su
  percentil p de los 730 días previos da mayor Sharpe y alfa > 0 frente a buy & hold
  en 2023-01 → 2025-09.
- Variantes fijadas (2026-10-13, antes de ver resultados): MVRV = CapMVRVCur de Coin
  Metrics (día d, conocido al cierre de d); fuera si MVRV_d > percentil p de los 730
  días previos (mín. 365); p ∈ {0,8; 0,9} → 2. Spot, costes 0,15 % por lado, 50/50
  BTC/ETH. Elegir p en 2020–2022 (Sharpe mensual). Aviso: datos de Coin Metrics
  no point-in-time (el MVRV se revisa menos que los flujos).

### H028 — Spread COIN-M vs USDT-M del mismo vencimiento
- Quién pierde: demanda segmentada (traders COIN-M y USDT-M distintos, con costes de
  mover colateral entre cuentas) que separa precios de contratos que liquidan igual.
- Predicción falsable: cuando el spread anualizado entre el trimestral COIN-M y el
  USDT-M del mismo vencimiento supera s, la posición contraria (corto el caro, largo el
  barato) hasta el vencimiento gana neto de 4 lados de costes de futuros.
- Variantes fijadas (2026-10-13, antes de ver resultados): BTC y ETH, vencimientos con
  ambos contratos (datos 1h limpios). Spread = CM_close/UM_close − 1, anualizado con los
  días restantes. Motor de H012 con la pata "spot" sustituida por el contrato barato:
  entrada si spread anualizado > s, salida al vencimiento o si < s/4; s ∈ {5 %, 10 %}
  y ambas direcciones (CM caro → corto CM/largo UM; UM caro → al revés) → 2 variantes
  (s), cada una con las dos direcciones. W = 0,5 por pata, costes 0,10 % por lado en
  ambas patas, sin liquidación modelada en la pata larga. Train: vencimientos ≤ 2022;
  OOS: 2023-01 → 2025-09.

### H029 — Diferencial de funding BTC vs ETH
- Quién pierde: los largos apalancados del activo con funding más caro.
- Predicción falsable: corto en el perp con mayor funding medio de 7 días y largo en el
  otro (0,5 por pata) cuando la diferencia supera d gana neto de costes y del movimiento
  relativo ETH/BTC, en 2023–2025.
- Variantes fijadas (2026-10-13, antes de ver resultados): semanal (lunes 00:00 UTC),
  funding equivalente 8 h de los 7 días previos; operar si |f_ETH − f_BTC| > d,
  d ∈ {0,5e-4; 1e-4} → 2. Costes 0,10 % por lado; funding real. Elegir d en 2020–2022.

### H030 — Reversión tras minutos extremos (cota bruta)
- Quién pierde: órdenes de mercado grandes e impacientes que empujan el precio más allá
  de su valor y pagan el rebote (proveedores de liquidez ganan).
- Predicción falsable: tras un minuto con |retorno| > k·σ (σ de los 1.440 minutos
  previos), el retorno de los H minutos siguientes tiene signo contrario y su media
  bruta supera el coste maker de ida y vuelta (0,04 %).
- Variantes fijadas (2026-10-13, antes de ver resultados): klines 1m de BTCUSDT y
  ETHUSDT perp, 2022 (train). k ∈ {4, 6} × H ∈ {5, 30} min → 4. Entrada en el open del
  minuto siguiente. Métrica: media bruta del retorno contrario y su t. Si ninguna supera
  0,04 % bruto con t > 3, se rechaza sin más datos (cota superior, como H014).

### H031 — Cambio de intervalo de funding (señal de apalancamiento extremo)
- Quién pierde: el lado apalancado (largos si el funding es positivo, cortos si es
  negativo) en el momento en que Binance considera su funding tan extremo como para
  liquidarlo cada 4 h o 1 h.
- Predicción falsable: tras el primer acortamiento del intervalo de funding de un perp,
  la posición contraria al lado que paga (corto si funding > 0, largo si < 0) durante N
  días gana neto de costes y funding, y bate a la misma operación en fechas aleatorias.
- Variantes fijadas (2026-10-13, antes de ver resultados): universo = todos los perps
  USDT-M (deslistados incluidos); evento = primer evento de funding cuyo
  funding_interval_hours es menor que el del evento anterior; signo = media de los 3
  últimos eventos (incluido el del cambio). Entrada en el open del día siguiente,
  N ∈ {3, 7} días → 2. Costes 0,15 % por lado; funding real; corto liquidado si high ≥
  2× entrada. Nulo: fechas aleatorias del mismo símbolo y misma dirección.
  Train = eventos 2023-01 → 2024-06; OOS = 2024-07 → 2025-09 (holdout intacto).
