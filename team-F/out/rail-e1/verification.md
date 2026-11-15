# Verificación de Rail — `rail-e1.arch`

## 1. Alcance

- Modelo: `models/rail-e1.arch` (sistema `Rail`, constituyente RLS).
- Versión del modelo: Model (M1) of the Rail Transportation System: starting structure (Delivery 1 with the corrections CR1 to CR4 of Delivery 2, section 2.2) and the properties of Delivery 2 (assumptions of section 4.3). Boundary components and global connectors are written as they appear in sos.arch. Latencies and periods in ms.
- Huella SHA-256 del archivo: `2230c7cceb3d`.
- Contenido: 32 componentes, 49 conectores, 7 análisis, 15 escenarios, 0 tácticas.
- Grafo C&C por tier: `graph.png`.
- Simulación: eventos discretos (colas FIFO con servicio exponencial, llegadas Poisson); réplicas independientes con semillas 1..n; IC 95 % con t de Student; resultado con margen del 10 % del umbral.
- Disponibilidad: Monte Carlo de fallas y reparaciones, 40 réplicas × 20 años, MTTR 4 h (supuesto), semillas 1000 + i; margen = 10 % de la indisponibilidad permitida.

## 2. Propiedades estructurales (grafo)

| Id | Propiedad | Escenario | Elementos encontrados | Resultado |
|----|-----------|-----------|-----------------------|-----------|
| S1 | Sin punto único de falla en la cadena de autorización C1 (FQS5AuthorizationAvailability, FQS5WithTrack) | F-QS5 (QS_F5) | CON, ILK, OBU, RAD, SAM, SEN | Violada |
| S1 (informativo) | Desglose: cadena de tierra (sin el equipo a bordo, T5) | F-QS5 (QS_F5) | CON, ILK, RAD, SAM | Violada |
| S2 | Sin conector bloqueante en el ciclo de autorización | F-QS4 (QS_F4) | ninguno | Satisfecha |
| S3 | Todo suministro hacia un T3 de la cadena de autorización (ILK, SAM) declara period | F-QS2/F-QS5 | F_K7 → SAM; F_K11 → ILK | Violada |
| S4 | SoS-K34 alcanza arribos-ms y hay un store entre la fuente de las unidades y el reconciliador | F-QS1 / SoS-QS1 | SoS_K34 no está en el modelo; arribos-ms no está en el modelo | Violada |

## 3. Escenarios simulados

### F-QS7 (QS_F7)

Corrida 1800 s, calentamiento 60 s, 10 (semillas 1–10); parámetro variado: —.

- Workload `Requests` (tasa 8/s): LGW → TRAD → RSV → TRAD → TRN → TRAD → POS → TRAD → LGW

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|-------|--------|------------|---------|--------|-----------|---------------------|
| — | p99_latency Requests | 1307.5 ms | [1236.2; 1378.8] | ≤ 800 ms | Violada | 10 (semillas 1–10) |

### F-QS3 (QS_F3)

Corrida 900 s, calentamiento 100 s, 20 (semillas 1–20); parámetro variado: —.

- Workload `Custody` (tasa 1/s): CRG → BRK → TRAD → LGW
- Workload `Burst` (tasa 244/s): CON → BRK

| Valor | Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |
|-------|--------|------------|---------|--------|-----------|---------------------|
| — | p99_latency Custody | 919.7 ms | [806.2; 1033.2] | ≤ 500 ms | Violada | 20 (semillas 1–20) |

## 4. Disponibilidad (Monte Carlo de fallas y reparaciones)

| Escenario | Análisis | Semilla | Réplicas | Estimación | IC 95 % | Conocido (fórmula Lab 3) | Umbral | Con margen desde | Resultado |
|---|---|---|---|---|---|---|---|---|---|
| F-QS5 | FQS5AuthorizationAvailability | 1000 | 40 × 20 años | 99.7866 % | [99.7769; 99.7963] | 99.7901 % | ≥ 99.95 % | 99.9550 % | Violada |
| F-QS5 | FQS5WithTrack | 1001 | 40 × 20 años | 99.6673 % | [99.6569; 99.6776] | 99.6804 % | ≥ 99.95 % | 99.9550 % | Violada |

## 5. Chequeo contra resultado conocido (Lab 5, §4.6)

| Caso | Fórmula | Conocido | Estimación | IC 95 % | ¿Dentro del IC? |
|------|---------|----------|------------|---------|-----------------|
| QS_F7 p99_latency Requests | ln(100)/(12 − 8) + constantes | 1311.3 ms | 1307.5 | [1236.2; 1378.8] | sí |
| QS_F3 p99_latency Custody | ln(100)/(250 − 245) + constantes | 1006.0 ms | 919.7 | [806.2; 1033.2] | sí |
| FQS5AuthorizationAvailability (MC, semilla 1000) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.7901 % | 99.7866 | [99.7769; 99.7963] | sí |
| FQS5WithTrack (MC, semilla 1001) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | 99.6804 % | 99.6673 | [99.6569; 99.6776] | no |

1 chequeo(s) fuera del IC. Con IC del 95 %, alrededor de 1 de cada 20 chequeos correctos cae fuera por azar; se reporta tal cual, sin cambiar semillas.

Los casos sin fórmula cerrada (p. ej. 0 < hit < 1: servicio hiperexponencial) no se listan.

## 6. Analítico de la Entrega 3 frente a simulado

| Escenario | Análisis E3 | Analítico E3 | Valor simulado | Estimación | IC 95 % | Observación |
|---|---|---|---|---|---|---|
| F-QS7 | FQS7CapacityRequest (p99) | 1400.5 ms | — | 1307.5 ms | [1236.2; 1378.8] | el analítico (Boole, cota) ≥ IC alto |
| F-QS3 | FQS3CustodyLatency (p99) | 1050.7 ms | — | 919.7 ms | [806.2; 1033.2] | el analítico (Boole, cota) ≥ IC alto |

## 7. Consistencia de `load` (análisis E3) con las tasas de los workloads

Aviso, no rechazo: la simulación toma las llegadas solo de los workloads; `load` lo usa el análisis de la Entrega 3.

| Escenario | Cola | capacity | load (E3) | Σ tasas de los workloads | Estado |
|---|---|---|---|---|---|
| QS_F7 | RSV | 12 | 8 | 8 | coincide |
| QS_F3 | BRK | 250 | 245 | 245 | coincide |

## 8. Análisis de la Entrega 3 nombrados en `verified_by`

Valor puntual del análisis, clasificado con margen del 10 % (del umbral, o de la indisponibilidad permitida).

| Escenario | Análisis | Métrica | Valor | Umbral | Resultado |
|---|---|---|---|---|---|
| F-QS7 (QS_F7) | FQS7CapacityRequest | latency | 1400.5 ms | ≤ 800 ms | Violada |
| F-QS3 (QS_F3) | FQS3CustodyLatency | latency | 1050.7 ms | ≤ 500 ms | Violada |
| F-QS1 (QS_F1) | SoSQS1M4 | latency | ilimitado | ≤ 900000 ms | Violada |
| F-QS2 (QS_F2) | FQS2SilentConcentrator | detection | ilimitado | ≤ 2000 ms | Violada |
| F-QS4 (QS_F4) | FQS4AuthorizationCycle | latency | 740.0 ms | ≤ 1000 ms | Satisfecha con margen |
| F-QS5 (QS_F5) | FQS5AuthorizationAvailability | availability | 99.7901 % | ≥ 99.95 % | Violada |
| F-QS5 (QS_F5) | FQS5WithTrack | availability | 99.6804 % | ≥ 99.95 % | Violada |
| SoS-QS1 (M4) (QS_SoS1) | SoSQS1M4 | latency | ilimitado | ≤ 900000 ms | Violada |

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

Ninguna declarada.
