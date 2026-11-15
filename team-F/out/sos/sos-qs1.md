# SoS-QS1 (M4): composición con las medidas verificadas (P11)

Modelo: `models/sos.arch`, análisis `SoSQS1M4`. Medida de SoS-QS1 M4: reconciliación ≤ 900 s tras recuperar Carretera. Los consumidores (CPS, PPS, RLS, FTS) reconcilian en paralelo después de los avisos SoS_K32, SoS_K33, SoS_K34, SoS_K35, cada uno con 300 s; `CGW` los representa en el análisis.

Clasificación (Laboratorio 5): con margen si el extremo alto del IC ≤ 0,9 · umbral; sin margen si ≤ umbral; violada si el extremo bajo > umbral; si no, inconclusa.

## 1. Bottom-up: medida verificada de cada tramo frente a su presupuesto

| Tramo | Dueño | Presupuesto | Medida verificada | IC 95 % | Fuente | Resultado |
|-------|-------|-------------|-------------------|---------|--------|-----------|
| RGW | RTS | 200 s | sin medida | — | presupuesto | — |
| SoS_K5 | acuerdo NCS/RTS | 40 s | sin medida | — | presupuesto | — |
| NCG | NCS | 230 s | 183,8 s | [183,3; 184,3] | equipo D, ncs-e4 (acuerdo conjunto) | satisfecha con margen |
| SoS_K32 | acuerdo CPS/NCS | 10 s | sin medida | — | presupuesto | — |
| CGW (consumidor) | CPS | 300 s | sin medida | — | presupuesto | — |
| PGW (consumidor) | PPS | 300 s | sin medida | — | presupuesto | — |
| LGW (consumidor) | RLS | 300 s | 144,9 s | [140,6; 149,3] | simulación, `out/rail-e3/verification.md` (P3, drain de F-QS1) | satisfecha con margen |
| FGW (consumidor) | FTS | 300 s | sin medida | — | presupuesto | — |

## 2. Top-down: composición frente a la medida de SoS-QS1

Composición: 200 + 40 + 230 + 10 + máx(consumidores). Con las medidas verificadas se suman los extremos de cada IC (cota conservadora de la media compuesta, no un IC de la suma); el máximo de los consumidores se toma extremo a extremo y un consumidor sin medida cuenta su presupuesto.

| Composición | NCS (alto) | máx(consumidores) (alto) | Total (media) | Total [bajo; alto] | Umbral | Resultado |
|-------------|-----|--------------------|---------------|--------------------|--------|-----------|
| Presupuestos (E2) | 230,0 s | 300,0 s | 780,0 s | [780,0; 780,0] | ≤ 900 s | satisfecha con margen |
| Medidas verificadas | 184,3 s | 300,0 s | 733,8 s | [733,3; 734,3] | ≤ 900 s | satisfecha con margen |
| NCS sin su rediseño (ncs-e2 de D) | 1.944,1 s | 300,0 s | 2.482,8 s | [2.471,5; 2.494,1] | ≤ 900 s | violada |

## 3. Sensibilidad a parámetros de otros dueños

Sobre la composición con medidas verificadas (extremo alto 734,3 s): holgura hasta violar 165,7 s; hasta perder el margen (0,9 · 900 = 810 s) 75,7 s. Cada fila varía un parámetro y deja los demás como están.

| Parámetro | Dueño | Valor actual | Con margen hasta | Violada por encima de | Crecimiento admisible |
|-----------|-------|--------------|------------------|-----------------------|-----------------------|
| RGW | RTS | 200,0 s (presupuesto) | 275,7 s | 365,7 s | +165,7 s (+83 %) |
| SoS_K5 | acuerdo NCS/RTS | 40,0 s (presupuesto) | 115,7 s | 205,7 s | +165,7 s (+414 %) |
| NCG | NCS | 184,3 s (medida) | 260,0 s | 350,0 s | +165,7 s (+90 %) |
| SoS_K32 | acuerdo CPS/NCS | 10,0 s (presupuesto) | 85,7 s | 175,7 s | +165,7 s (+1.657 %) |
| máx(consumidores) | CPS, PPS, RLS, FTS | 300,0 s | 375,7 s | 465,7 s | +165,7 s (+55 %) |

Férreo: su extremo alto (149,3 s) queda 150,7 s por debajo del presupuesto de los demás consumidores (300 s), así que no fija el máximo del grupo; mientras los demás estén en su presupuesto, SoS-QS1 conserva el margen con el férreo hasta 375,7 s y se viola por encima de 465,7 s.
