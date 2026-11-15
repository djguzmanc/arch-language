# Verificación de Rail — `rail-e3.arch`

## Resumen por propiedad

Resultado en las categorías del Lab 5 (con margen, sin margen, inconclusa, violada) y no verificable. Las propiedades estructurales y las de umbral 0 (lost) no tienen margen: «Satisfecha». «No evaluable»: al modelo le faltan los elementos que la propiedad usa. P5, P8–P11 son valores puntuales del análisis de la Entrega 3 (sin IC).

| Id | Propiedad | Escenario | Técnica | Estimación | IC 95 % | Umbral | Resultado |
|---|---|---|---|---|---|---|---|
| S1 | Sin punto único de falla en la cadena de autorización C1 (OBU incluida) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | G (grafo) | CON, ILK, OBU | — | 0 elementos | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | G (grafo) | ninguno | — | 0 elementos | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización declara period | F-QS2/F-QS5: T3 ILK, SAM, SAMB | G (grafo) | F_K7 → SAM; F_K37 → SAMB | — | 0 elementos | Violada |
| S4 | SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que falla en F-QS1 | F-QS1 / SoS-QS1 | G (grafo) | camino NCG → LGW → TRAD → ARR; store ARRDB justo antes de ARR (falla) en Units | — | camino y store | Satisfecha |
| P1 | p99 de la solicitud de capacidad (F-QS7) | F-QS7 (QS_F7) | SIM (DES), valor del modelo 1; sensibilidad en §3 | 204.5 ms | [203.1; 205.9] | ≤ 800 ms | Satisfecha con margen |
| P2 | p99 de la custodia durante la ráfaga (F-QS3) | F-QS3 (QS_F3) | SIM (DES) | 204.0 ms | [194.6; 213.4] | ≤ 500 ms | Satisfecha con margen |
| P3 | Reconciliación (drain) tras la caída de 4 h (F-QS1) | F-QS1 (QS_F1) | SIM (DES), valor del modelo 1.667; sensibilidad en §3 | 145.0 s | [140.7; 149.3] | ≤ 300 s | Satisfecha con margen |
| P4 | Unidades perdidas en la caída (F-QS1) | F-QS1 (QS_F1) | SIM (DES), valor del modelo 1.667; sensibilidad en §3 | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha |
| P5 | Detección de datos viejos (F-QS1) | F-QS1 (detección) | AN (E3) | 180.0 s | — (valor puntual) | ≤ 240 s | Satisfecha con margen |
| P6 | Disponibilidad de la cadena C1 (F-QS5) | F-QS5 | MC (1000 × 20 años, semilla 1000); Lab 3 = 99.9699 % como conocido | 99.9701 % | [99.9694; 99.9708] | ≥ 99.95 % | Satisfecha con margen |
| P7 | Disponibilidad de C1 con la vía (F-QS5) | F-QS5 | MC (1000 × 20 años, semilla 1001); Lab 3 = 99.8599 % como conocido | 99.8581 % | [99.8565; 99.8597] | ≥ 99.95 % | Violada |
| P8 | Toma de control de SAM-B (F-QS5) | F-QS5 (toma de control) | AN (E3) | 2500.0 ms | — (valor puntual) | ≤ 5000 ms | Satisfecha con margen |
| P9 | Detección del concentrador callado (F-QS2) | F-QS2 | AN (E3) | 1500.0 ms | — (valor puntual) | ≤ 2000 ms | Satisfecha con margen |
| P10 | Ciclo de autorización p99 (F-QS4) | F-QS4 | AN (E3) | 780.0 ms | — (valor puntual) | ≤ 1000 ms | Satisfecha con margen |
| P11 | SoS-QS1 M4 compuesto (presupuestos; P3 bottom-up) | SoS-QS1 (M4) | AN (presupuestos E3); bottom-up: P3 = 145.0 s, IC [140.7; 149.3] frente a 300 s (Satisfecha con margen); composición en out/sos/sos-qs1.md | 780.0 s | — (valor puntual) | ≤ 900 s | Satisfecha con margen |
| QS_F7R | F-QS7 (0 solicitudes sin respuesta) | rendimiento | — | — | — | — | No verificable: Timeouts y reintentos en el workload (300 ms y un reintento, Entrega 2 §8.2); parcial: fracción con latencia > 300 ms |
| QS_F3T | F-QS3 (cola de telemetría) | rendimiento | — | — | — | — | No verificable: Tasas que cambian en el tiempo (ráfaga de 15 min y luego carga normal) y canales con prioridad en el broker: 30.600 eventos, ~160 s de drenaje |
| QS_F1C | F-QS1 (0 trenes cancelados) | resiliencia | — | — | — | — | No verificable: Reglas de comportamiento (despacho con la ETA estimada más 30 min de holgura) y model checking sobre la máquina de estados del despacho |
| QS_F1Q | F-QS1 (≤ 2 consultas/s por SoS-K18a) | resiliencia | — | — | — | — | No verificable: Limitador de tasa por conector (tasa máxima acordada en SoS-K18a como restricción y su medida); en la simulación la tasa de consultas es un parámetro de entrada |
| QS_F2R | F-QS2 (0 rutas sobre estado de más de 2 s) | tolerancia a fallas | — | — | — | — | No verificable: Máquina de estados del enclavamiento (edad del estado por sección) y model checking |
| QS_F4A | F-QS4 (0 autoridades o reportes falsos aceptados) | seguridad | — | — | — | — | No verificable: Identidad, credenciales y límites de confianza por conector; model checking del protocolo de autenticación |
| QS_F6 | F-QS6 | evolucionabilidad | — | — | — | — | No verificable: Versiones de interfaz por conector, período de convivencia y comparación de dos modelos (change impact) para contar los componentes tocados y los mensajes rechazados por versión; despliegue en caliente. C7 da evidencia parcial: todo pasa por TRAD |
| QS_SoS1M1 | SoS-QS1 (M1: 0 trenes cancelados) | resiliencia | — | — | — | — | No verificable: Reglas de comportamiento (P5); model checking sobre la máquina de estados del despacho |
| QS_SoS1M2 | SoS-QS1 (M2: error de ETA ≤ ±30 min p95) | resiliencia | — | — | — | — | No verificable: Distribución del error de estimación de la ETA y su simulación |

## 1. Alcance

- Modelo: `models/rail-e3.arch` (sistema `Rail`, constituyente RLS).
- Versión del modelo: of the new data, arribos-ms); 0 messages rejected by version during the coexistence; deployment without stopping the Rail Gateway.
- Huella SHA-256 del archivo: `4e488e74b58f`.
- Contenido: 38 componentes, 64 conectores, 9 análisis, 16 escenarios, 9 tácticas.
- Grafo C&C por tier: `graph.png`.
- Simulación: eventos discretos (colas FIFO con servicio exponencial, llegadas Poisson); réplicas independientes con semillas 1..n; IC 95 % con t de Student; resultado con margen del 10 % del umbral.
- Disponibilidad: Monte Carlo de fallas y reparaciones, 1000 réplicas × 20 años, MTTR 4 h (supuesto), semillas 1000 + i; margen = 10 % de la indisponibilidad permitida.

## 2. Propiedades estructurales (grafo)

| Id | Propiedad | Escenario | Elementos encontrados | Resultado |
|----|-----------|-----------|-----------------------|-----------|
| S1 | Sin punto único de falla en la cadena de autorización C1 (OBU incluida) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | CON, ILK, OBU | Violada |
| S1 (informativo) | Desglose: cadena de tierra (sin el equipo a bordo, T5) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | CON, ILK | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | ninguno | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización declara period | F-QS2/F-QS5: T3 ILK, SAM, SAMB | F_K7 → SAM; F_K37 → SAMB | Violada |
| S4 | SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que falla en F-QS1 | F-QS1 / SoS-QS1 | camino NCG → LGW → TRAD → ARR; store ARRDB justo antes de ARR (falla) en Units | Satisfecha |

## 3. Escenarios simulados

### F-QS7 (QS_F7)

Corrida 1800 s, calentamiento 60 s, 10 (semillas 1–10); parámetro variado: hit de F_K38a (modelo: 1).

- Workload `Requests` (tasa 8/s): LGW → TRAD → [RSV reads CACHE | TRN | POS] → TRAD → LGW

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|---|---|---|---|---|---|---|
| 1 | p99_latency Requests | 204.5 ms | [203.1; 205.9] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.9 | p99_latency Requests | 346.4 ms | [338.9; 353.8] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.8 | p99_latency Requests | 424.5 ms | [411.3; 437.6] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.7 | p99_latency Requests | 493.8 ms | [480.7; 507.0] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.6 | p99_latency Requests | 564.4 ms | [547.4; 581.3] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.5 | p99_latency Requests | 648.4 ms | [617.6; 679.3] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.4 | p99_latency Requests | 736.0 ms | [700.2; 771.8] | ≤ 800 ms | Satisfecha sin margen | 10 (semillas 1–10) |
| 0.2 | p99_latency Requests | 943.8 ms | [890.0; 997.7] | ≤ 800 ms | Violada | 10 (semillas 1–10) |
| 0 | p99_latency Requests | 1275.2 ms | [1185.7; 1364.8] | ≤ 800 ms | Violada | 10 (semillas 1–10) |

### F-QS3 (QS_F3)

Corrida 900 s, calentamiento 100 s, 10 (semillas 1–10); parámetro variado: —.

- Workload `Custody` (tasa 1/s): CRG → BRK → TRAD → LGW
- Workload `Access` (tasa 10/s): CON → BRK

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|---|---|---|---|---|---|---|
| — | p99_latency Custody | 204.0 ms | [194.6; 213.4] | ≤ 500 ms | Satisfecha con margen | 10 (semillas 1–10) |

### F-QS1 (QS_F1)

Corrida 16000 s, calentamiento 0 s, 20 (semillas 1–20); parámetro variado: capacity de ARR (modelo: 1.667).

- Workload `Units` (tasa 0.016667/s): ARRDB → ARR → TRAD → LGW
- Falla: ARR caído desde 0 s durante 14400 s
- q_ef (consultas/s efectivas) derivada de la capacity de ARR con la fórmula documentada en el modelo (comentario de la línea 71): capacity = 1/(1/q + 0.1 s), es decir q_ef = 1/(1/capacity − 0.1 s). Supuesto declarado del modelo (los comentarios no son parte del metamodelo).

| Valor | q_ef (consultas/s) | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|---|---|---|---|---|---|---|---|
| 1.667 | 2.00 | drain Units | 145.0 s | [140.7; 149.3] | ≤ 300 s | Satisfecha con margen | 20 (semillas 1–20) |
| 1.667 | 2.00 | lost Units | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha | 20 (semillas 1–20) |
| 1.25 | 1.43 | drain Units | 193.3 s | [187.6; 199.0] | ≤ 300 s | Satisfecha con margen | 20 (semillas 1–20) |
| 1.25 | 1.43 | lost Units | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha | 20 (semillas 1–20) |
| 1 | 1.11 | drain Units | 241.6 s | [234.4; 248.8] | ≤ 300 s | Satisfecha con margen | 20 (semillas 1–20) |
| 1 | 1.11 | lost Units | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha | 20 (semillas 1–20) |
| 0.909 | 1.00 | drain Units | 265.8 s | [257.9; 273.7] | ≤ 300 s | Satisfecha sin margen | 20 (semillas 1–20) |
| 0.909 | 1.00 | lost Units | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha | 20 (semillas 1–20) |
| 0.85 | 0.93 | drain Units | 284.2 s | [275.8; 292.7] | ≤ 300 s | Satisfecha sin margen | 20 (semillas 1–20) |
| 0.85 | 0.93 | lost Units | 0.0 events | [0.0; 0.0] | ≤ 0 events | Satisfecha | 20 (semillas 1–20) |

## 4. Disponibilidad (Monte Carlo de fallas y reparaciones)

| Escenario | Análisis | Semilla | Réplicas | Estimación | IC 95 % | Conocido (fórmula Lab 3) | Umbral | Con margen desde | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| F-QS5 | FQS5AuthorizationAvailability | 1000 | 1000 × 20 años | 99.9701 % | [99.9694; 99.9708] | 99.9699 % | ≥ 99.95 % | 99.9550 % | Satisfecha con margen |
| F-QS5 | FQS5WithTrack | 1001 | 1000 × 20 años | 99.8581 % | [99.8565; 99.8597] | 99.8599 % | ≥ 99.95 % | 99.9550 % | Violada |

## 5. Chequeo contra resultado conocido (Lab 5, §4.6)

| Caso | Fórmula | Conocido | Estimación | IC 95 % | ¿Dentro del IC? |
|------|---------|----------|------------|---------|-----------------|
| QS_F7 p99_latency Requests (1) | ln(100)/(40 − 8) + constantes | 203.9 ms | 204.5 | [203.1; 205.9] | sí |
| QS_F7 p99_latency Requests (0) | ln(100)/(12 − 8) + constantes | 1211.3 ms | 1275.2 | [1185.7; 1364.8] | sí |
| QS_F3 p99_latency Custody | ln(100)/(50 − 11) + constantes | 203.1 ms | 204.0 | [194.6; 213.4] | sí |
| QS_F1 drain Units (1.667) | E[N]/μ = 240.005/1.667 + constantes | 144.0 s | 145.0 | [140.7; 149.3] | sí |
| QS_F1 drain Units (1.667) | E[N]/(μ − λ) = 240.005/(1.667 − 0.016667) (L5) | 145.5 s | 145.0 | [140.7; 149.3] | sí |
| QS_F1 lost Units (1.667) | store retiene: 0 | 0.0 events | 0.0 | [0.0; 0.0] | sí |
| QS_F1 drain Units (1.25) | E[N]/μ = 240.005/1.25 + constantes | 192.1 s | 193.3 | [187.6; 199.0] | sí |
| QS_F1 drain Units (1.25) | E[N]/(μ − λ) = 240.005/(1.25 − 0.016667) (L5) | 194.7 s | 193.3 | [187.6; 199.0] | sí |
| QS_F1 lost Units (1.25) | store retiene: 0 | 0.0 events | 0.0 | [0.0; 0.0] | sí |
| QS_F1 drain Units (1) | E[N]/μ = 240.005/1 + constantes | 240.1 s | 241.6 | [234.4; 248.8] | sí |
| QS_F1 drain Units (1) | E[N]/(μ − λ) = 240.005/(1 − 0.016667) (L5) | 244.1 s | 241.6 | [234.4; 248.8] | sí |
| QS_F1 lost Units (1) | store retiene: 0 | 0.0 events | 0.0 | [0.0; 0.0] | sí |
| QS_F1 drain Units (0.909) | E[N]/μ = 240.005/0.909 + constantes | 264.1 s | 265.8 | [257.9; 273.7] | sí |
| QS_F1 drain Units (0.909) | E[N]/(μ − λ) = 240.005/(0.909 − 0.016667) (L5) | 269.0 s | 265.8 | [257.9; 273.7] | sí |
| QS_F1 lost Units (0.909) | store retiene: 0 | 0.0 events | 0.0 | [0.0; 0.0] | sí |
| QS_F1 drain Units (0.85) | E[N]/μ = 240.005/0.85 + constantes | 282.4 s | 284.2 | [275.8; 292.7] | sí |
| QS_F1 drain Units (0.85) | E[N]/(μ − λ) = 240.005/(0.85 − 0.016667) (L5) | 288.1 s | 284.2 | [275.8; 292.7] | sí |
| QS_F1 lost Units (0.85) | store retiene: 0 | 0.0 events | 0.0 | [0.0; 0.0] | sí |
| FQS5AuthorizationAvailability (MC, semilla 1000) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.9699 % | 99.9701 | [99.9694; 99.9708] | sí |
| FQS5WithTrack (MC, semilla 1001) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.8599 % | 99.8581 | [99.8565; 99.8597] | no |

1 chequeo(s) fuera del IC. Con IC del 95 %, alrededor de 1 de cada 20 chequeos correctos cae fuera por azar; se reporta tal cual, sin cambiar semillas.

Los casos sin fórmula cerrada (p. ej. 0 < hit < 1: servicio hiperexponencial) no se listan.

## 6. Analítico de la Entrega 3 frente a simulado

| Escenario | Análisis E3 | Analítico E3 | Valor simulado | Estimación | IC 95 % | Observación |
|---|---|---|---|---|---|---|
| F-QS7 | FQS7CapacityRequest (p99) | 215.1 ms | 1 | 204.5 ms | [203.1; 205.9] | el analítico (Boole, cota) ≥ IC alto |
| F-QS3 | FQS3CustodyLatency (p99) | 208.8 ms | — | 204.0 ms | [194.6; 213.4] | el analítico cae en el IC |

## 7. Consistencia de `load` (análisis E3) con las tasas de los workloads

Aviso, no rechazo: la simulación toma las llegadas solo de los workloads; `load` lo usa el análisis de la Entrega 3.

| Escenario | Cola | capacity | load (E3) | Σ tasas de los workloads | Estado |
|---|---|---|---|---|---|
| QS_F7 | RSV | 12 | 8 | 8 | coincide |
| QS_F3 | BRK | 50 | 11 | 11 | coincide |
| QS_F1 | ARR | 1.667 | 0.016667 | 0.016667 | coincide |

## 8. Análisis de la Entrega 3 nombrados en `verified_by`

Valor puntual del análisis, clasificado con margen del 10 % (del umbral, o de la indisponibilidad permitida). **Informativo**: cuando la propiedad se simula o se estima por Monte Carlo (disponibilidad: §4), el veredicto es el de la simulación o el MC; aquí el analítico es solo referencia (resultado conocido o cota).

| Escenario | Análisis | Métrica | Valor | Umbral | Resultado |
|---|---|---|---|---|---|
| F-QS7 (QS_F7) | FQS7CapacityRequest | latency | 215.1 ms | ≤ 800 ms | Satisfecha con margen |
| F-QS3 (QS_F3) | FQS3CustodyLatency | latency | 208.8 ms | ≤ 500 ms | Satisfecha con margen |
| F-QS1 (QS_F1) | FQS1StaleData | detection | 180000.0 ms | ≤ 240000 ms | Satisfecha con margen |
| F-QS2 (QS_F2) | FQS2SilentConcentrator | detection | 1500.0 ms | ≤ 2000 ms | Satisfecha con margen |
| F-QS4 (QS_F4) | FQS4AuthorizationCycle | latency | 780.0 ms | ≤ 1000 ms | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5AuthorizationAvailability | availability | 99.9699 % | ≥ 99.95 % | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5WithTrack | availability | 99.8599 % | ≥ 99.95 % | Violada |
| F-QS5 (QS_F5) | FQS5Takeover | detection | 2500.0 ms | ≤ 5000 ms | Satisfecha con margen |
| SoS-QS1 (M4) (QS_SoS1) | SoSQS1M4 | latency | 780000.0 ms | ≤ 900000 ms | Satisfecha con margen |

## 9. Escenarios no verificables con este lenguaje

| Escenario | Atributo | Qué falta |
|---|---|---|
| F-QS7 (0 solicitudes sin respuesta) (QS_F7R) | rendimiento | Timeouts y reintentos en el workload (300 ms y un reintento, Entrega 2 §8.2); parcial: fracción con latencia > 300 ms |
| F-QS3 (cola de telemetría) (QS_F3T) | rendimiento | Tasas que cambian en el tiempo (ráfaga de 15 min y luego carga normal) y canales con prioridad en el broker: 30.600 eventos, ~160 s de drenaje |
| F-QS1 (0 trenes cancelados) (QS_F1C) | resiliencia | Reglas de comportamiento (despacho con la ETA estimada más 30 min de holgura) y model checking sobre la máquina de estados del despacho |
| F-QS1 (≤ 2 consultas/s por SoS-K18a) (QS_F1Q) | resiliencia | Limitador de tasa por conector (tasa máxima acordada en SoS-K18a como restricción y su medida); en la simulación la tasa de consultas es un parámetro de entrada |
| F-QS2 (0 rutas sobre estado de más de 2 s) (QS_F2R) | tolerancia a fallas | Máquina de estados del enclavamiento (edad del estado por sección) y model checking |
| F-QS4 (0 autoridades o reportes falsos aceptados) (QS_F4A) | seguridad | Identidad, credenciales y límites de confianza por conector; model checking del protocolo de autenticación |
| F-QS6 (QS_F6) | evolucionabilidad | Versiones de interfaz por conector, período de convivencia y comparación de dos modelos (change impact) para contar los componentes tocados y los mensajes rechazados por versión; despliegue en caliente. C7 da evidencia parcial: todo pasa por TRAD |
| SoS-QS1 (M1: 0 trenes cancelados) (QS_SoS1M1) | resiliencia | Reglas de comportamiento (P5); model checking sobre la máquina de estados del despacho |
| SoS-QS1 (M2: error de ETA ≤ ±30 min p95) (QS_SoS1M2) | resiliencia | Distribución del error de estimación de la ETA y su simulación |

## 10. Tácticas declaradas

| Táctica | Para | Introduce | Cambia |
|---|---|---|---|
| Caché de capacidad precalculada (T_Cache) | F-QS7 | CACHE, F_K38a, F_K38b, F_K39 | RSV |
| Llamadas en paralelo a los servicios de C4, timeout de 300 ms y un reintento (T_Parallel) | F-QS7 | — | LGW, F_K23a, F_K23b |
| Canal crítico reservado en el broker (50 eventos/s) (T_CriticalChannel) | F-QS3 | — | BRK, F_K12, F_K19, F_K21 |
| Modo degradado con reconciliación y límite de consultas (2/s) (T_Degraded) | F-QS1, SoS-QS1 (M4) | ARR, ARRDB, F_K28a, F_K28b, F_K29, F_K30, F_K31, F_K32, F_K33, SoS_K34 | LGW, TRAD, PLN |
| Resumen periódico con marca de tiempo del concentrador (0,4 s) (T_Heartbeat) | F-QS2 | — | CON, F_K11, ILK, F_K6 |
| Autenticación y cifrado del canal tren-tierra; descarte de duplicados (T_Authentication) | F-QS4 | — | OBU, SAM, RAD, F_K13a, F_K13b |
| Segundo camino de radio (T_RadioB) | F-QS5 | RADB, F_K34a, F_K34b | OBU |
| Segunda medición de sensores (T_SensorsB) | F-QS5 | SENB, F_K35 | OBU |
| SAM de respaldo en espera caliente con latido (T_SAMB) | F-QS5 | SAMB, F_K36, F_K37 | SAM |

## 11. Prueba de regresión del simulador (orden FIFO con forks)

Workload A: [Q1 | Q2 alcanzada 0,5 s después]; workload B directo a Q2 (5/s; Q2 atiende 10/s y recibe 6/s). Cada cola debe atender sus llegadas en orden de tiempo: la estancia media de B en Q2 es la de una M/M/1, 1/(10 − 6) = 0,25 s, con o sin el retardo de A.

| Retardo de A hacia Q2 | Estancia media de B | IC 95 % | Conocido | ¿Dentro? |
|---|---|---|---|---|
| 0.5 s | 0.2523 s | [0.2480; 0.2566] | 0.25 s | sí |
| 0 s | 0.2514 s | [0.2469; 0.2560] | 0.25 s | sí |

RLS_RECONCILIATION_S 144.95 140.65 149.25
