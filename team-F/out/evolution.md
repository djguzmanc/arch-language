# Evolución de las propiedades por iteración

Generado por verification.py al verificar varios modelos en una corrida. Cada celda: resultado (estimación). «—»: la propiedad no aplica a ese modelo.

| Id | Propiedad | rail-e1 | rail-e2 | rail-e3 | rail-e4 |
|---|---|---|---|---|---|
| S1 | Sin punto único de falla en la cadena de autorización C1 (OBU incluida) | Violada | Violada | Violada | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | Satisfecha | Satisfecha | Satisfecha | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización declara period | Violada | Violada | Violada | Satisfecha |
| S4 | SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que falla en F-QS1 | No evaluable | No evaluable | Satisfecha | Satisfecha |
| P1 | p99 de la solicitud de capacidad (F-QS7) | Violada (1307.5 ms) | Satisfecha con margen (204.5 ms) | Satisfecha con margen (204.5 ms) | Satisfecha con margen (204.5 ms) |
| P2 | p99 de la custodia durante la ráfaga (F-QS3) | Violada (919.7 ms) | Satisfecha con margen (204.0 ms) | Satisfecha con margen (204.0 ms) | Satisfecha con margen (204.0 ms) |
| P3 | Reconciliación (drain) tras la caída de 4 h (F-QS1) | — | — | Satisfecha con margen (145.0 s) | Satisfecha con margen (108.5 s) |
| P4 | Unidades perdidas en la caída (F-QS1) | — | — | Satisfecha (0.0 events) | Satisfecha (0.0 events) |
| P5 | Detección de datos viejos (F-QS1) | — | — | Satisfecha con margen (180.0 s) | Satisfecha con margen (180.0 s) |
| P6 | Disponibilidad de la cadena C1 (F-QS5) | Violada (99.7911 %) | Satisfecha con margen (99.9701 %) | Satisfecha con margen (99.9701 %) | Satisfecha con margen (99.9701 %) |
| P7 | Disponibilidad de C1 con la vía (F-QS5) | Violada (99.6808 %) | Violada (99.8581 %) | Violada (99.8581 %) | Satisfecha con margen (99.9581 %) |
| P8 | Toma de control de SAM-B (F-QS5) | — | Satisfecha con margen (2500.0 ms) | Satisfecha con margen (2500.0 ms) | Satisfecha con margen (2500.0 ms) |
| P9 | Detección del concentrador callado (F-QS2) | Violada (ilimitado) | Satisfecha con margen (1500.0 ms) | Satisfecha con margen (1500.0 ms) | Satisfecha con margen (1500.0 ms) |
| P9b | Detección del estado de rutas callado (F-QS2, it. 4) | — | — | — | Satisfecha con margen (1320.0 ms) |
| P10 | Ciclo de autorización p99 (F-QS4) | Satisfecha con margen (740.0 ms) | Satisfecha con margen (780.0 ms) | Satisfecha con margen (780.0 ms) | Satisfecha con margen (780.0 ms) |
| P11 | SoS-QS1 M4 compuesto (presupuestos; P3 bottom-up) | Violada (ilimitado) | Satisfecha con margen (780.0 s) | Satisfecha con margen (780.0 s) | Satisfecha con margen (780.0 s) |
| QS_F7R | F-QS7 (0 solicitudes sin respuesta) | No verificable | No verificable | No verificable | No verificable |
| QS_F3T | F-QS3 (cola de telemetría) | No verificable | No verificable | No verificable | No verificable |
| QS_F1 | F-QS1 | No verificable | No verificable | — | — |
| QS_F1C | F-QS1 (0 trenes cancelados) | No verificable | No verificable | No verificable | No verificable |
| QS_F1Q | F-QS1 (≤ 2 consultas/s por SoS-K18a) | No verificable | No verificable | No verificable | No verificable |
| QS_F2R | F-QS2 (0 rutas sobre estado de más de 2 s) | No verificable | No verificable | No verificable | No verificable |
| QS_F4A | F-QS4 (0 autoridades o reportes falsos aceptados) | No verificable | No verificable | No verificable | No verificable |
| QS_F6 | F-QS6 | No verificable | No verificable | No verificable | No verificable |
| QS_SoS1M1 | SoS-QS1 (M1: 0 trenes cancelados) | No verificable | No verificable | No verificable | No verificable |
| QS_SoS1M2 | SoS-QS1 (M2: error de ETA ≤ ±30 min p95) | No verificable | No verificable | No verificable | No verificable |
