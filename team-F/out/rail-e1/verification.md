# Verificación de Rail — `rail-e1.arch`

## Resumen por propiedad

Resultado en las categorías del Lab 5 (con margen, sin margen, inconclusa, violada) y no verificable. Las propiedades estructurales y las de umbral 0 (lost) no tienen margen: «Satisfecha». «No evaluable»: al modelo le faltan los elementos que la propiedad usa. P5, P8–P11 son valores puntuales del análisis de la Entrega 3 (sin IC).

| Id | Propiedad | Escenario | Técnica | Estimación | IC 95 % | Umbral | Resultado |
|---|---|---|---|---|---|---|---|
| S1 | Sin punto único de falla en la cadena de autorización C1 (OBU incluida) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | G (grafo) | CON, ILK, OBU, RAD, SAM, SEN | — | 0 elementos | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | G (grafo) | ninguno | — | 0 elementos | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización declara period | F-QS2/F-QS5: T3 ILK, SAM | G (grafo) | F_K7 → SAM; F_K11 → ILK | — | 0 elementos | Violada |
| S4 | SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que falla en F-QS1 | F-QS1 / SoS-QS1 | G (grafo) | faltan en el modelo: SoS_K34, arribos-ms, escenario F-QS1 simulado con su falla | — | camino y store | No evaluable |
| P1 | p99 de la solicitud de capacidad (F-QS7) | F-QS7 (QS_F7) | SIM (DES) | 1307.5 ms | [1236.2; 1378.8] | ≤ 800 ms | Violada |
| P2 | p99 de la custodia durante la ráfaga (F-QS3) | F-QS3 (QS_F3) | SIM (DES) | 919.7 ms | [808.1; 1031.2] | ≤ 500 ms | Violada |
| P6 | Disponibilidad de la cadena C1 (F-QS5) | F-QS5 | MC (1000 × 20 años, semilla 1000); Lab 3 = 99.7901 % como conocido | 99.7911 % | [99.7891; 99.7931] | ≥ 99.95 % | Violada |
| P7 | Disponibilidad de C1 con la vía (F-QS5) | F-QS5 | MC (1000 × 20 años, semilla 1001); Lab 3 = 99.6804 % como conocido | 99.6808 % | [99.6784; 99.6832] | ≥ 99.95 % | Violada |
| P9 | Detección del concentrador callado (F-QS2) | F-QS2 | AN (E3) | ilimitado | — (valor puntual) | ≤ 2 s | Violada |
| P10 | Ciclo de autorización p99 (F-QS4) | F-QS4 | AN (E3) | 740.0 ms | — (valor puntual) | ≤ 1000 ms | Satisfecha con margen |
| P11 | SoS-QS1 M4 compuesto (presupuestos; P3 bottom-up) | SoS-QS1 (M4) | AN (presupuestos E3); bottom-up: P3 sin simular; composición en out/sos/sos-qs1.md | ilimitado | — (valor puntual) | ≤ 900 s | Violada |
| QS_F7R | F-QS7 (0 solicitudes sin respuesta) | rendimiento | — | — | — | — | No verificable: Timeouts y reintentos en el workload (300 ms y un reintento, Entrega 2 §8.2); parcial: fracción con latencia > 300 ms |
| QS_F3T | F-QS3 (cola de telemetría) | rendimiento | — | — | — | — | No verificable: Tasas que cambian en el tiempo (ráfaga de 15 min y luego carga normal) y canales con prioridad en el broker: 30.600 eventos, ~160 s de drenaje |
| QS_F1 | F-QS1 | resiliencia | — | — | — | — | No verificable: La estructura de partida no tiene arribos-ms, arribos-db ni SoS-K34 (Entrega 2 §6.1): no hay detección ni reconciliación que analizar o simular; se agregan en rail-e2 y sus parámetros en rail-e3 |
| QS_F1C | F-QS1 (0 trenes cancelados) | resiliencia | — | — | — | — | No verificable: Reglas de comportamiento (despacho con la ETA estimada más 30 min de holgura) y model checking sobre la máquina de estados del despacho |
| QS_F1Q | F-QS1 (≤ 2 consultas/s por SoS-K18a) | resiliencia | — | — | — | — | No verificable: Limitador de tasa por conector (tasa máxima acordada en SoS-K18a como restricción y su medida); en la simulación la tasa de consultas es un parámetro de entrada |
| QS_F2R | F-QS2 (0 rutas sobre estado de más de 2 s) | tolerancia a fallas | — | — | — | — | No verificable: Máquina de estados del enclavamiento (edad del estado por sección) y model checking |
| QS_F4A | F-QS4 (0 autoridades o reportes falsos aceptados) | seguridad | — | — | — | — | No verificable: Identidad, credenciales y límites de confianza por conector; model checking del protocolo de autenticación |
| QS_F6 | F-QS6 | evolucionabilidad | — | — | — | — | No verificable: Versiones de interfaz por conector, período de convivencia y comparación de dos modelos (change impact) para contar los componentes tocados y los mensajes rechazados por versión; despliegue en caliente. C7 da evidencia parcial: todo pasa por TRAD |
| QS_SoS1M1 | SoS-QS1 (M1: 0 trenes cancelados) | resiliencia | — | — | — | — | No verificable: Reglas de comportamiento (P5); model checking sobre la máquina de estados del despacho |
| QS_SoS1M2 | SoS-QS1 (M2: error de ETA ≤ ±30 min p95) | resiliencia | — | — | — | — | No verificable: Distribución del error de estimación de la ETA y su simulación |

## 1. Alcance

- Modelo: `models/rail-e1.arch` (sistema `Rail`, constituyente RLS).
- Versión del modelo: Model (M1) of the Rail Transportation System: starting structure (Delivery 1 with the corrections CR1 to CR4 of Delivery 2, section 2.2) and the properties of Delivery 2 (assumptions of section 4.3). Boundary components and global connectors are written as they appear in sos.arch. Latencies and periods in ms.
- Huella SHA-256 del archivo: `f65e3787ce6d`.
- Contenido: 32 componentes, 49 conectores, 7 análisis, 16 escenarios, 0 tácticas.
- Grafo C&C por tier: `graph.png`.
- Simulación: eventos discretos (colas FIFO con servicio exponencial, llegadas Poisson); réplicas independientes con semillas 1..n; IC 95 % con t de Student; resultado con margen del 10 % del umbral.
- Disponibilidad: Monte Carlo de fallas y reparaciones, 1000 réplicas × 20 años, MTTR 4 h (supuesto), semillas 1000 + i; margen = 10 % de la indisponibilidad permitida.

## 2. Propiedades estructurales (grafo)

| Id | Propiedad | Escenario | Elementos encontrados | Resultado |
|----|-----------|-----------|-----------------------|-----------|
| S1 | Sin punto único de falla en la cadena de autorización C1 (OBU incluida) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | CON, ILK, OBU, RAD, SAM, SEN | Violada |
| S1 (informativo) | Desglose: cadena de tierra (sin el equipo a bordo, T5) | F-QS5 (QS_F5): FQS5AuthorizationAvailability, FQS5WithTrack | CON, ILK, RAD, SAM | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | ninguno | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización declara period | F-QS2/F-QS5: T3 ILK, SAM | F_K7 → SAM; F_K11 → ILK | Violada |
| S4 | SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que falla en F-QS1 | F-QS1 / SoS-QS1 | faltan en el modelo: SoS_K34, arribos-ms, escenario F-QS1 simulado con su falla | No evaluable |

## 3. Escenarios simulados

### F-QS7 (QS_F7)

Corrida 1800 s, calentamiento 60 s, 10 (semillas 1–10); parámetro variado: —.

- Workload `Requests` (tasa 8/s): LGW → TRAD → RSV → TRAD → TRN → TRAD → POS → TRAD → LGW

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|---|---|---|---|---|---|---|
| — | p99_latency Requests | 1307.5 ms | [1236.2; 1378.8] | ≤ 800 ms | Violada | 10 (semillas 1–10) |

### F-QS3 (QS_F3)

Corrida 900 s, calentamiento 100 s, 20 (semillas 1–20); parámetro variado: —.

- Workload `Custody` (tasa 1/s): CRG → BRK → TRAD → LGW
- Workload `Burst` (tasa 244/s): CON → BRK

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|---|---|---|---|---|---|---|
| — | p99_latency Custody | 919.7 ms | [808.1; 1031.2] | ≤ 500 ms | Violada | 20 (semillas 1–20) |

## 4. Disponibilidad (Monte Carlo de fallas y reparaciones)

| Escenario | Análisis | Semilla | Réplicas | Estimación | IC 95 % | Conocido (fórmula Lab 3) | Umbral | Con margen desde | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| F-QS5 | FQS5AuthorizationAvailability | 1000 | 1000 × 20 años | 99.7911 % | [99.7891; 99.7931] | 99.7901 % | ≥ 99.95 % | 99.9550 % | Violada |
| F-QS5 | FQS5WithTrack | 1001 | 1000 × 20 años | 99.6808 % | [99.6784; 99.6832] | 99.6804 % | ≥ 99.95 % | 99.9550 % | Violada |

## 5. Chequeo contra resultado conocido (Lab 5, §4.6)

| Caso | Fórmula | Conocido | Estimación | IC 95 % | ¿Dentro del IC? |
|------|---------|----------|------------|---------|-----------------|
| QS_F7 p99_latency Requests | ln(100)/(12 − 8) + constantes | 1311.3 ms | 1307.5 | [1236.2; 1378.8] | sí |
| QS_F3 p99_latency Custody | ln(100)/(250 − 245) + constantes | 1006.0 ms | 919.7 | [808.1; 1031.2] | sí |
| FQS5AuthorizationAvailability (MC, semilla 1000) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.7901 % | 99.7911 | [99.7891; 99.7931] | sí |
| FQS5WithTrack (MC, semilla 1001) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.6804 % | 99.6808 | [99.6784; 99.6832] | sí |

Los casos sin fórmula cerrada (p. ej. 0 < hit < 1: servicio hiperexponencial) no se listan.

## 6. Analítico de la Entrega 3 frente a simulado

| Escenario | Análisis E3 | Analítico E3 | Valor simulado | Estimación | IC 95 % | Observación |
|---|---|---|---|---|---|---|
| F-QS7 | FQS7CapacityRequest (p99) | 1400.5 ms | — | 1307.5 ms | [1236.2; 1378.8] | el analítico (Boole, cota) ≥ IC alto |
| F-QS3 | FQS3CustodyLatency (p99) | 1050.7 ms | — | 919.7 ms | [808.1; 1031.2] | el analítico (Boole, cota) ≥ IC alto |

## 7. Consistencia de `load` (análisis E3) con las tasas de los workloads

Aviso, no rechazo: la simulación toma las llegadas solo de los workloads; `load` lo usa el análisis de la Entrega 3.

| Escenario | Cola | capacity | load (E3) | Σ tasas de los workloads | Estado |
|---|---|---|---|---|---|
| QS_F7 | RSV | 12 | 8 | 8 | coincide |
| QS_F3 | BRK | 250 | 245 | 245 | coincide |

## 8. Análisis de la Entrega 3 nombrados en `verified_by`

Valor puntual del análisis, clasificado con margen del 10 % (del umbral, o de la indisponibilidad permitida). **Informativo**: cuando la propiedad se simula o se estima por Monte Carlo (disponibilidad: §4), el veredicto es el de la simulación o el MC; aquí el analítico es solo referencia (resultado conocido o cota).

| Escenario | Análisis | Métrica | Valor | Umbral | Resultado |
|---|---|---|---|---|---|
| F-QS7 (QS_F7) | FQS7CapacityRequest | latency | 1400.5 ms | ≤ 800 ms | Violada |
| F-QS3 (QS_F3) | FQS3CustodyLatency | latency | 1050.7 ms | ≤ 500 ms | Violada |
| F-QS2 (QS_F2) | FQS2SilentConcentrator | detection | ilimitado | ≤ 2000 ms | Violada |
| F-QS4 (QS_F4) | FQS4AuthorizationCycle | latency | 740.0 ms | ≤ 1000 ms | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5AuthorizationAvailability | availability | 99.7901 % | ≥ 99.95 % | Violada |
| F-QS5 (QS_F5) | FQS5WithTrack | availability | 99.6804 % | ≥ 99.95 % | Violada |
| SoS-QS1 (M4) (QS_SoS1) | SoSQS1M4 | latency | ilimitado | ≤ 900000 ms | Violada |

## 9. Escenarios no verificables con este lenguaje

| Escenario | Atributo | Qué falta |
|---|---|---|
| F-QS7 (0 solicitudes sin respuesta) (QS_F7R) | rendimiento | Timeouts y reintentos en el workload (300 ms y un reintento, Entrega 2 §8.2); parcial: fracción con latencia > 300 ms |
| F-QS3 (cola de telemetría) (QS_F3T) | rendimiento | Tasas que cambian en el tiempo (ráfaga de 15 min y luego carga normal) y canales con prioridad en el broker: 30.600 eventos, ~160 s de drenaje |
| F-QS1 (QS_F1) | resiliencia | La estructura de partida no tiene arribos-ms, arribos-db ni SoS-K34 (Entrega 2 §6.1): no hay detección ni reconciliación que analizar o simular; se agregan en rail-e2 y sus parámetros en rail-e3 |
| F-QS1 (0 trenes cancelados) (QS_F1C) | resiliencia | Reglas de comportamiento (despacho con la ETA estimada más 30 min de holgura) y model checking sobre la máquina de estados del despacho |
| F-QS1 (≤ 2 consultas/s por SoS-K18a) (QS_F1Q) | resiliencia | Limitador de tasa por conector (tasa máxima acordada en SoS-K18a como restricción y su medida); en la simulación la tasa de consultas es un parámetro de entrada |
| F-QS2 (0 rutas sobre estado de más de 2 s) (QS_F2R) | tolerancia a fallas | Máquina de estados del enclavamiento (edad del estado por sección) y model checking |
| F-QS4 (0 autoridades o reportes falsos aceptados) (QS_F4A) | seguridad | Identidad, credenciales y límites de confianza por conector; model checking del protocolo de autenticación |
| F-QS6 (QS_F6) | evolucionabilidad | Versiones de interfaz por conector, período de convivencia y comparación de dos modelos (change impact) para contar los componentes tocados y los mensajes rechazados por versión; despliegue en caliente. C7 da evidencia parcial: todo pasa por TRAD |
| SoS-QS1 (M1: 0 trenes cancelados) (QS_SoS1M1) | resiliencia | Reglas de comportamiento (P5); model checking sobre la máquina de estados del despacho |
| SoS-QS1 (M2: error de ETA ≤ ±30 min p95) (QS_SoS1M2) | resiliencia | Distribución del error de estimación de la ETA y su simulación |

## 10. Tácticas declaradas

Ninguna declarada.

## 11. Prueba de regresión del simulador (orden FIFO con forks)

Workload A: [Q1 | Q2 alcanzada 0,5 s después]; workload B directo a Q2 (5/s; Q2 atiende 10/s y recibe 6/s). Cada cola debe atender sus llegadas en orden de tiempo: la estancia media de B en Q2 es la de una M/M/1, 1/(10 − 6) = 0,25 s, con o sin el retardo de A.

| Retardo de A hacia Q2 | Estancia media de B | IC 95 % | Conocido | ¿Dentro? |
|---|---|---|---|---|
| 0.5 s | 0.2523 s | [0.2480; 0.2566] | 0.25 s | sí |
| 0 s | 0.2514 s | [0.2469; 0.2560] | 0.25 s | sí |
