# Analysis of Rail

## FQS3CustodyLatency (Scenario F-QS3)

| Stage | Budget |
|-------|--------|
| F_K19 | 25 ms |
| BRK | queue: mean 1/(50 − 11) = 25.6 ms; p99.2 = 4.83 × mean = 123.8 ms |
| TRAD | 60 ms |

Chain latency p99: **209 ms**; target 500: **met**

## FQS4AuthorizationCycle (Scenario F-QS4)

| Stage | Budget |
|-------|--------|
| OBU | 80 ms |
| F_K13a | 250 ms |
| SAM | 120 ms |
| F_K13b | 250 ms |
| OBU | 80 ms |

Chain latency p99: **780 ms**; target 1000: **met**

## FQS5AuthorizationAvailability (Scenario F-QS5)

| Factor | Unavailability | Share |
|--------|----------------|-------|
| SEN, SENB (β = 0.1) | 0.0050 % | 17 % |
| OBU | 0.0100 % | 33 % |
| RAD, RADB (β = 0.1) | 0.0101 % | 33 % |
| SAM, SAMB (β = 0.1) | 0.0050 % | 17 % |

Chain availability: **99.97 %** (2.6 h/year); target 99.95: **met**

## FQS5WithTrack (Scenario F-QS5 (con vía))

| Factor | Unavailability | Share |
|--------|----------------|-------|
| SEN, SENB (β = 0.1) | 0.0050 % | 4 % |
| OBU | 0.0100 % | 7 % |
| RAD, RADB (β = 0.1) | 0.0101 % | 7 % |
| SAM, SAMB (β = 0.1) | 0.0050 % | 4 % |
| ILK | 0.0100 % | 7 % |
| CON | 0.1000 % | 71 % |

Chain availability: **99.86 %** (12.3 h/year); target 99.95: **NOT met**

## FQS7CapacityRequest (Scenario F-QS7)

| Stage | Budget |
|-------|--------|
| RSV (queue: mean 1/(40 − 8) = 31.2 ms; p99.3 = 4.96 × mean = 155.1 ms) ‖ TRN (50 ms) ‖ POS (50 ms) | 155.1 ms (maximum, in parallel) |
| TRAD | 60 ms |

Chain latency p99: **215 ms**; target 800: **met**

## FQS2SilentConcentrator (Scenario F-QS2)

| Stage | Budget |
|-------|--------|
| F_K11 | 1200 ms |
| ILK | 300 ms |

Chain latency: **1500 ms**; target 2000: **met**

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200000 ms |
| SoS_K5 | 40000 ms |
| NCG | 230000 ms |
| SoS_K34 | 10000 ms (budget) |
| CGW (300000 ms) ‖ ARR (300000 ms (budget)) | 300000.0 ms (maximum, in parallel) |

Chain latency: **780000 ms**; target 900000: **met**

## Silent supply into availability chains

| Connector | Feeds | Information carried |
|-----------|-------|---------------------|
| F_K7 | SAM | Estado de rutas, agujas y señales cuando cambian |
| F_K9 | CON | Paso de trenes y ocupación de secciones, en el formato de cada fabricante |
| F_K10 | CON | Identificación de vagones y contenedores al entrar y salir de la terminal |
| F_K14 | OBU | Velocidad, distancia recorrida y condiciones físicas del tren |
| F_K35 | OBU | Velocidad y distancia, segunda medición |
| F_K37 | SAMB | Estado de rutas hacia el respaldo |
