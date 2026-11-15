# Tácticas de las iteraciones 2 y 4 (equipo F)

## 1. Contribución de cada táctica de la Entrega 2 a P1 (F-QS7, rail-e2)

10 réplicas (semillas 1–10), corrida 1800 s, calentamiento 60 s; umbral ≤ 800 ms. Sin caché = hit 0 en F_K38a. Sin paralelo = las ramas del fork del modelo en serie: LGW → TRAD → RSV reads CACHE → TRAD → TRN → TRAD → POS → TRAD → LGW. El resultado conocido sale de known_result sobre el plan de cada variante (una cola M/M/1 más las constantes).

| Estructura | Estimación | IC 95 % | Conocido | ¿Dentro? | Resultado |
|---|---|---|---|---|---|
| rail-e2: caché + paralelo (hit 1) | 204.5 ms | [203.1; 205.9] | 203.9 ms | sí | Satisfecha con margen |
| sin caché (hit 0), con paralelo | 1275.2 ms | [1185.7; 1364.8] | 1211.3 ms | sí | Violada |
| con caché (hit 1), sin paralelo (camino en serie) | 304.5 ms | [303.1; 305.9] | 303.9 ms | sí | Satisfecha con margen |
| sin caché ni paralelo (≈ rail-e1) | 1375.2 ms | [1285.7; 1464.8] | 1311.3 ms | sí | Violada |

## 2. Contribución de T4.1 a P7 (F-QS5 con vía, rail-e4)

Monte Carlo 1000 réplicas × 20 años, MTTR 4 h, semilla 1001 en todas las variantes (números aleatorios comunes; la última fila reproduce la de out/rail-e4). Umbral ≥ 99.95 %; con margen desde 99.9550 %.

| Estructura | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |
|---|---|---|---|---|---|
| rail-e3: sin T4.1 (ILK y CON únicos) | 99.8581 % | [99.8565; 99.8597] | 99.8599 % | no | Violada |
| solo CONB (ILK único) | 99.9491 % | [99.9481; 99.9501] | 99.9498 % | sí | Inconclusa |
| solo ILKB (CON único) | 99.8682 % | [99.8667; 99.8698] | 99.8689 % | sí | Violada |
| rail-e4: CONB + ILKB (T4.1) | 99.9581 % | [99.9572; 99.9590] | 99.9588 % | sí | Satisfecha con margen |

## 3. Sensibilidad de P7 a β (rail-e4, todos los grupos con el mismo β)

| β | Semilla | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |
|---|---|---|---|---|---|---|
| 0.00 | 1200 | 99.9899 % | [99.9895; 99.9903] | 99.9897 % | sí | Satisfecha con margen |
| 0.02 | 1201 | 99.9835 % | [99.9830; 99.9840] | 99.9836 % | sí | Satisfecha con margen |
| 0.05 | 1202 | 99.9741 % | [99.9734; 99.9748] | 99.9743 % | sí | Satisfecha con margen |
| 0.08 | 1203 | 99.9650 % | [99.9642; 99.9658] | 99.9650 % | sí | Satisfecha con margen |
| 0.10 | 1204 | 99.9584 % | [99.9576; 99.9593] | 99.9588 % | sí | Satisfecha con margen |
| 0.12 | 1205 | 99.9530 % | [99.9521; 99.9539] | 99.9526 % | sí | Satisfecha sin margen |
| 0.15 | 1206 | 99.9433 % | [99.9423; 99.9442] | 99.9433 % | sí | Violada |
| 0.20 | 1207 | 99.9278 % | [99.9267; 99.9289] | 99.9279 % | sí | Violada |

Según la fórmula del Lab 3, P7 cumple el umbral (99.95 %) mientras β ≤ 0.128 y lo cumple con margen (99.955 %) mientras β ≤ 0.112. El MC clasifica por el extremo bajo del IC, que es más exigente que el valor puntual.

