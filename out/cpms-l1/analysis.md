# Analysis of CPMS

## ExitAvailability (Scenario A-QS2)

| Factor | Unavailability | Share |
|--------|----------------|-------|
| T3.6 | 0.0500 % | 17 % |
| T3.9 | 0.0500 % | 17 % |
| CGW | 0.0500 % | 17 % |
| SoS_K12a | 0.0500 % | 17 % |
| NCG | 0.1000 % | 33 % |

Chain availability: **99.70 %** (26.2 h/year); target 99.9: **NOT met**

## ExitAvailabilityD2Before (Scenario A-QS2 (D2 before))

| Factor | Unavailability | Share |
|--------|----------------|-------|
| T3.6 × 2 (β = 0.05) | 0.0025 % | 2 % |
| T3.9 × 2 (β = 0.05) | 0.0025 % | 2 % |
| CGW × 2 (β = 0.05) | 0.0025 % | 2 % |
| SoS_K12a | 0.0500 % | 32 % |
| NCG | 0.1000 % | 63 % |

Chain availability: **99.84 %** (13.8 h/year); target 99.9: **NOT met**

## FieldEventLoad (Scenario A-QS4)

| Element | Load (per s) | Capacity per instance (per s) | Instances | Utilization | Instances needed |
|---------|--------------|-------------------------------|-----------|-------------|------------------|
| T2.5 | 20 | 10 | 1 | 200 % | 2 |

Bottleneck utilization: **200 %**; target 100: **NOT met**

## ConsolidatedStateQueries (Scenario A-QS6)

| Element | Load (per s) | Capacity per instance (per s) | Instances | Utilization | Instances needed |
|---------|--------------|-------------------------------|-----------|-------------|------------------|
| SoS_K21a | 1.5 | 2 | 1 | 75 % | 1 |

Bottleneck utilization: **75 %**; target 100: **met**

## FieldEventLatency (Scenario A-QS4 (latency))

| Stage | Budget |
|-------|--------|
| A-K1 | 50 ms |
| A-K5 | 50 ms |
| A-K22 | 50 ms |

Chain latency: **150 ms**; target 200: **met**

## PortReconciliation (Scenario A-QS6 (reconciliation))

| Stage | Budget |
|-------|--------|
| CGW | 60 s |

Composed deadline: **60 s**; target 300: **met**

## PortReconciliationRetry (Scenario A-QS6 (reconciliation, one retry per query))

| Stage | Budget |
|-------|--------|
| CGW | 120 s |

Composed deadline: **120 s**; target 300: **met**

## SoSQS1M4 (Scenario SoS-QS1 (M4))

| Stage | Budget |
|-------|--------|
| RGW | 200000 ms |
| SoS_K5 | 40000 ms |
| NCG | 230000 ms |
| SoS_K32 | 10000 ms |
| CGW | 300000 ms |

Chain latency: **780000 ms**; target 900000: **met**
