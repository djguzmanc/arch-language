# Verificación de Rail — `rail-e2.arch`

## 1. Alcance

- Modelo: `models/rail-e2.arch` (sistema `Rail`, constituyente RLS).
- Versión del modelo: Model (M1) of the Rail Transportation System: resulting structure of Delivery 2 (section 7: 6 components added and 10 modified; 15 internal connectors and SoS-K34 added).
- Huella SHA-256 del archivo: `687e8e032aca`.
- Contenido: 38 componentes, 64 conectores, 8 análisis, 15 escenarios, 9 tácticas.
- Grafo C&C por tier: `graph.png`.
- Simulación: eventos discretos (colas FIFO con servicio exponencial, llegadas Poisson); réplicas independientes con semillas 1..n; IC 95 % con t de Student; resultado con margen del 10 % del umbral.
- Disponibilidad: Monte Carlo de fallas y reparaciones, 40 réplicas × 20 años, MTTR 4 h (supuesto), semillas 1000 + i; margen = 10 % de la indisponibilidad permitida.

## 2. Propiedades estructurales (grafo)

| Id | Propiedad | Escenario | Elementos encontrados | Resultado |
|----|-----------|-----------|-----------------------|-----------|
| S1 | Sin punto único de falla en la cadena de autorización C1 (FQS5AuthorizationAvailability, FQS5WithTrack) | F-QS5 (QS_F5) | CON, ILK, OBU | Violada |
| S1 (informativo) | Desglose: cadena de tierra (sin el equipo a bordo, T5) | F-QS5 (QS_F5) | CON, ILK | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | ninguno | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización (ILK, SAM, SAMB) declara period | F-QS2/F-QS5 | F_K7 → SAM; F_K37 → SAMB | Violada |
| S4 | SoS-K34 alcanza arribos-ms y hay un store entre la fuente de las unidades y el reconciliador | F-QS1 / SoS-QS1 | camino NCG → LGW → TRAD → ARR; ningún store conectado a ARR | Violada |

## 3. Escenarios simulados

### F-QS7 (QS_F7)

Corrida 1800 s, calentamiento 60 s, 10 (semillas 1–10); parámetro variado: hit de F_K38a (modelo: 1).

- Workload `Requests` (tasa 8/s): LGW → TRAD → [RSV reads CACHE | TRN | POS] → TRAD → LGW

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|-------|--------|------------|---------|--------|-----------|---------------------|
| 1 | p99_latency Requests | 204.5 ms | [203.1; 205.9] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.9 | p99_latency Requests | 346.4 ms | [339.0; 353.8] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.8 | p99_latency Requests | 424.5 ms | [411.3; 437.6] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.7 | p99_latency Requests | 493.8 ms | [480.7; 507.0] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.6 | p99_latency Requests | 564.4 ms | [547.4; 581.3] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.5 | p99_latency Requests | 648.4 ms | [617.6; 679.2] | ≤ 800 ms | Satisfecha con margen | 10 (semillas 1–10) |
| 0.4 | p99_latency Requests | 736.0 ms | [700.2; 771.8] | ≤ 800 ms | Satisfecha sin margen | 10 (semillas 1–10) |
| 0.2 | p99_latency Requests | 943.8 ms | [890.0; 997.6] | ≤ 800 ms | Violada | 10 (semillas 1–10) |
| 0 | p99_latency Requests | 1275.2 ms | [1185.7; 1364.7] | ≤ 800 ms | Violada | 10 (semillas 1–10) |

### F-QS3 (QS_F3)

Corrida 900 s, calentamiento 100 s, 10 (semillas 1–10); parámetro variado: —.

- Workload `Custody` (tasa 1/s): CRG → BRK → TRAD → LGW
- Workload `Access` (tasa 10/s): CON → BRK

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|-------|--------|------------|---------|--------|-----------|---------------------|
| — | p99_latency Custody | 204.0 ms | [194.6; 213.4] | ≤ 500 ms | Satisfecha con margen | 10 (semillas 1–10) |

## 4. Disponibilidad (Monte Carlo de fallas y reparaciones)

| Escenario | Análisis | Semilla | Réplicas | Estimación | IC 95 % | Conocido (fórmula Lab 3) | Umbral | Con margen desde | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| F-QS5 | FQS5AuthorizationAvailability | 1000 | 40 × 20 años | 99.9728 % | [99.9693; 99.9762] | 99.9699 % | ≥ 99.95 % | 99.9550 % | Satisfecha con margen |
| F-QS5 | FQS5WithTrack | 1001 | 40 × 20 años | 99.8622 % | [99.8521; 99.8723] | 99.8599 % | ≥ 99.95 % | 99.9550 % | Violada |

## 5. Chequeo contra resultado conocido (Lab 5, §4.6)

| Caso | Fórmula | Conocido | Estimación | IC 95 % | ¿Dentro del IC? |
|------|---------|----------|------------|---------|-----------------|
| QS_F7 p99_latency Requests (1) | ln(100)/(40 − 8) + constantes | 203.9 ms | 204.5 | [203.1; 205.9] | sí |
| QS_F7 p99_latency Requests (0) | ln(100)/(12 − 8) + constantes | 1211.3 ms | 1275.2 | [1185.7; 1364.7] | sí |
| QS_F3 p99_latency Custody | ln(100)/(50 − 11) + constantes | 203.1 ms | 204.0 | [194.6; 213.4] | sí |
| FQS5AuthorizationAvailability (MC, semilla 1000) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.9699 % | 99.9728 | [99.9693; 99.9762] | sí |
| FQS5WithTrack (MC, semilla 1001) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.8599 % | 99.8622 | [99.8521; 99.8723] | sí |

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

## 8. Análisis de la Entrega 3 nombrados en `verified_by`

Valor puntual del análisis, clasificado con margen del 10 % (del umbral, o de la indisponibilidad permitida).

| Escenario | Análisis | Métrica | Valor | Umbral | Resultado |
|---|---|---|---|---|---|
| F-QS7 (QS_F7) | FQS7CapacityRequest | latency | 215.1 ms | ≤ 800 ms | Satisfecha con margen |
| F-QS3 (QS_F3) | FQS3CustodyLatency | latency | 208.8 ms | ≤ 500 ms | Satisfecha con margen |
| F-QS1 (QS_F1) | SoSQS1M4 | latency | 780000.0 ms | ≤ 900000 ms | Satisfecha con margen |
| F-QS2 (QS_F2) | FQS2SilentConcentrator | detection | 1500.0 ms | ≤ 2000 ms | Satisfecha con margen |
| F-QS4 (QS_F4) | FQS4AuthorizationCycle | latency | 780.0 ms | ≤ 1000 ms | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5AuthorizationAvailability | availability | 99.9699 % | ≥ 99.95 % | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5WithTrack | availability | 99.8599 % | ≥ 99.95 % | Violada |
| F-QS5 (QS_F5) | FQS5Takeover | detection | 2500.0 ms | ≤ 5000 ms | Satisfecha con margen |
| SoS-QS1 (M4) (QS_SoS1) | SoSQS1M4 | latency | 780000.0 ms | ≤ 900000 ms | Satisfecha con margen |

## 9. Escenarios no verificables con este lenguaje

| Escenario | Atributo | Qué falta |
|---|---|---|
| F-QS7 (0 sin respuesta; tope de 660 ms) (QS_F7R) | rendimiento | Timeouts y reintentos en el workload (300 ms y un reintento, Entrega 2 §8.2); parcial: fracción con latencia > 300 ms |
| F-QS3 (cola de telemetría) (QS_F3T) | rendimiento | Tasas que cambian en el tiempo (ráfaga de 15 min y luego carga normal) y canales con prioridad en el broker: 30.600 eventos, ~160 s de drenaje |
| F-QS1 (0 trenes cancelados) (QS_F1C) | resiliencia | Reglas de comportamiento (regla de corte del despacho) y model checking sobre la máquina de estados del despacho |
| F-QS2 (0 rutas sobre estado viejo) (QS_F2R) | tolerancia a fallas | Máquina de estados del enclavamiento y model checking |
| F-QS4 (0 falsos aceptados) (QS_F4A) | seguridad | Identidad, credenciales y límites de confianza por conector; model checking del protocolo de autenticación |
| F-QS6 (QS_F6) | evolucionabilidad | Versiones de interfaz por conector y comparación de dos modelos (change impact); C7 da evidencia parcial: todo pasa por TRAD |
| SoS-QS1 (M1) (QS_SoS1M1) | resiliencia | Reglas de comportamiento (P5); model checking sobre la máquina de estados del despacho |
| SoS-QS1 (M2) (QS_SoS1M2) | resiliencia | Distribución del error de estimación de la ETA y su simulación |

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
