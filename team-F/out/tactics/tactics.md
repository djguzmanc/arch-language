# Tácticas de las iteraciones 2 y 4 (equipo F)

## 1. Contribución de cada táctica de la Entrega 2 a P1 (F-QS7, rail-e2)

10 réplicas (semillas 1–10), corrida 1800 s, calentamiento 60 s; umbral ≤ 800 ms.

| Estructura | Estimación | IC 95 % | Conocido | ¿Dentro? | Resultado |
|---|---|---|---|---|---|
| rail-e2: caché + paralelo (hit 1) | 204.5 ms | [203.1; 205.9] | 203.9 ms | sí | Satisfecha con margen |
| sin caché (hit 0), con paralelo | 1275.2 ms | [1185.7; 1364.7] | 1211.3 ms | sí | Violada |
| con caché (hit 1), sin paralelo (camino secuencial) | 304.5 ms | [303.1; 305.9] | 303.9 ms | sí | Satisfecha con margen |
| sin caché ni paralelo (≈ rail-e1) | 1375.2 ms | [1285.7; 1464.7] | 1311.3 ms | sí | Violada |

## 2. Contribución de T4.1 a P7 (F-QS5 con vía, rail-e4)

Monte Carlo 40 réplicas × 20 años, MTTR 4 h, semilla 1001 en todas las variantes (números aleatorios comunes; la última fila reproduce la de out/rail-e4). Umbral ≥ 99.95 %; con margen desde 99.9550 %.

| Estructura | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |
|---|---|---|---|---|---|
| rail-e3: sin T4.1 (ILK y CON únicos) | 99.8622 % | [99.8521; 99.8723] | 99.8599 % | sí | Violada |
| solo CONB (ILK único) | 99.9506 % | [99.9452; 99.9560] | 99.9498 % | sí | Inconclusa |
| solo ILKB (CON único) | 99.8673 % | [99.8608; 99.8738] | 99.8689 % | sí | Violada |
| rail-e4: CONB + ILKB (T4.1) | 99.9572 % | [99.9530; 99.9614] | 99.9588 % | sí | Satisfecha sin margen |

## 3. Sensibilidad de P7 a β (rail-e4, todos los grupos con el mismo β)

| β | Semilla | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |
|---|---|---|---|---|---|---|
| 0.00 | 1200 | 99.9891 % | [99.9870; 99.9911] | 99.9897 % | sí | Satisfecha con margen |
| 0.02 | 1201 | 99.9841 % | [99.9811; 99.9870] | 99.9836 % | sí | Satisfecha con margen |
| 0.05 | 1202 | 99.9738 % | [99.9701; 99.9774] | 99.9743 % | sí | Satisfecha con margen |
| 0.08 | 1203 | 99.9666 % | [99.9626; 99.9705] | 99.9650 % | sí | Satisfecha con margen |
| 0.10 | 1204 | 99.9585 % | [99.9540; 99.9630] | 99.9588 % | sí | Satisfecha sin margen |
| 0.12 | 1205 | 99.9466 % | [99.9416; 99.9516] | 99.9526 % | no | Inconclusa |
| 0.15 | 1206 | 99.9449 % | [99.9390; 99.9508] | 99.9433 % | sí | Inconclusa |
| 0.20 | 1207 | 99.9252 % | [99.9191; 99.9312] | 99.9279 % | sí | Violada |

Según la fórmula del Lab 3, P7 cumple el umbral (99.95 %) mientras β ≤ 0.128 y lo cumple con margen (99.955 %) mientras β ≤ 0.112. El MC clasifica por el extremo bajo del IC, que es más exigente que el valor puntual.

