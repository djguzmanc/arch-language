# Analysis of Rail

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200000 ms |
| SoS_K5 | 40000 ms |
| NCG | 230000 ms |
| SoS_K32 | 10000 ms |
| CGW (300000 ms) ‖ CRG (unbounded) | unbounded (maximum, in parallel) |

Chain latency: **unbounded**; target 900000: **NOT met**

## FQS3CustodyLatency (Scenario F-QS3)

| Stage | Budget |
|-------|--------|
| F_K19 | 25 ms |
| BRK | queue: mean 1/(250 − 245) = 200.0 ms; p99.2 = 4.83 × mean = 965.7 ms |
| TRAD | 60 ms |

Chain latency p99: **1051 ms**; target 500: **NOT met**

## FQS4AuthorizationCycle (Scenario F-QS4)

| Stage | Budget |
|-------|--------|
| OBU | 80 ms |
| F_K13a | 230 ms |
| SAM | 120 ms |
| F_K13b | 230 ms |
| OBU | 80 ms |

Chain latency p99: **740 ms**; target 1000: **met**

## FQS5AuthorizationAvailability (Scenario F-QS5)

| Factor | Unavailability | Share |
|--------|----------------|-------|
| SEN | 0.0500 % | 24 % |
| OBU | 0.0100 % | 5 % |
| RAD | 0.1000 % | 48 % |
| SAM | 0.0500 % | 24 % |

Chain availability: **99.79 %** (18.4 h/year); target 99.95: **NOT met**

## FQS5WithTrack (Scenario F-QS5 (con vía))

| Factor | Unavailability | Share |
|--------|----------------|-------|
| SEN | 0.0500 % | 16 % |
| OBU | 0.0100 % | 3 % |
| RAD | 0.1000 % | 31 % |
| SAM | 0.0500 % | 16 % |
| ILK | 0.0100 % | 3 % |
| CON | 0.1000 % | 31 % |

Chain availability: **99.68 %** (28.0 h/year); target 99.95: **NOT met**

## FQS2SilentConcentrator (Scenario F-QS2)

| Stage | Budget |
|-------|--------|
| F_K11 | unbounded |
| ILK | 300 ms |

Chain latency: **unbounded**; target 2000: **NOT met**

## FQS7CapacityRequest (Scenario F-QS7)

| Stage | Budget |
|-------|--------|
| RSV | queue: mean 1/(12 − 8) = 250.0 ms; p99.3 = 4.96 × mean = 1240.5 ms |
| TRN | 50 ms |
| POS | 50 ms |
| TRAD | 60 ms |

Chain latency p99: **1400 ms**; target 800: **NOT met**

## Silent supply into availability chains

| Connector | Feeds | Information carried |
|-----------|-------|---------------------|
| F_K7 | SAM | Estado de rutas, agujas y señales cuando cambian |
| F_K9 | CON | Paso de trenes y ocupación de secciones, en el formato de cada fabricante |
| F_K10 | CON | Identificación de vagones y contenedores al entrar y salir de la terminal |
| F_K11 | ILK | Ocupación de secciones de vía en el formato interno, solo cuando cambia (A11) |
| F_K14 | OBU | Velocidad, distancia recorrida y condiciones físicas del tren |
