# SoS-QS1 (M4): composición con las medidas verificadas (P11)

Modelo: `models/sos.arch`, análisis `SoSQS1M4`. Medida de SoS-QS1 M4: reconciliación ≤ 900 s tras recuperar Carretera. Los consumidores (CPS, PPS, RLS, FTS) reconcilian en paralelo después de los avisos SoS_K32, SoS_K33, SoS_K34, SoS_K35, cada uno con 300 s; `CGW` los representa en el análisis.

Clasificación (Laboratorio 5): con margen si el extremo alto del IC ≤ 0,9 · umbral; sin margen si ≤ umbral; violada si el extremo bajo > umbral; si no, inconclusa.

## 1. Bottom-up: medida verificada de cada tramo frente a su presupuesto

| Tramo | Dueño | Presupuesto | Medida verificada | IC 95 % | Fuente | Resultado |
|-------|-------|-------------|-------------------|---------|--------|-----------|
| RGW | RTS | 200 s | sin medida | — | presupuesto | — |
| SoS_K5 | acuerdo NCS/RTS | 40 s | sin medida | — | presupuesto | — |
| NCG | NCS | 230 s | 183,8 s | [183,3; 184,3] | acuerdo conjunto, sección 1.3.3 (documento común) | satisfecha con margen |
| SoS_K32 | acuerdo CPS/NCS | 10 s | sin medida | — | presupuesto | — |
| CGW (consumidor) | CPS | 300 s | sin medida | — | presupuesto | — |
| PGW (consumidor) | PPS | 300 s | sin medida | — | presupuesto | — |
| LGW (consumidor) | RLS | 300 s | 108,5 s | [102,9; 114,1] | simulación, `out/rail-e4/verification.md` (P3, drain de F-QS1) | satisfecha con margen |
| LGW (consumidor), evolución: antes del rediseño (T4.3) | RLS | 300 s | 144,9 s | [140,7; 149,2] | simulación, `out/rail-e3/verification.md` (no entra en la composición) | satisfecha con margen |
| FGW (consumidor) | FTS | 300 s | sin medida | — | presupuesto | — |

Nota sobre el NCS: el repositorio del equipo D (`out/ncs-e4/verification.md`) publica para ncs-e4 184,9 s, IC [183,8; 186,1], y no 183,8 s [183,3; 184,3] como el acuerdo conjunto. La diferencia no cambia ninguna conclusión de este reporte (la holgura de SoS-QS1 es de más de 160 s) y debe resolverse en el acuerdo. `--ncs` cambia la cifra.

Nota sobre el férreo: T4.3 (reconciliación por camión) supone que SoS-K18a devuelve todas las unidades de un camión en una sola consulta; está por confirmar en el acuerdo conjunto. Si no se confirma, la cifra de rail-e3 (antes del rediseño) es la conservadora.

Definiciones distintas: el tramo del férreo es nuestro `drain` (desde el fin de la falla hasta que sale el último trabajo retenido) y el del NCS es el `recovery` del equipo D (Laboratorio 5), que además cuenta la espera de la primera llegada posterior a la falla (≈ 1/λ). Se componen tal como están: según el equipo D esa espera es de 0,67 s en su cuello de botella (CAR), así que la suma no cambia de forma apreciable, pero no son la misma medida.

## 2. Top-down: composición frente a la medida de SoS-QS1

Composición: 200 + 40 + 230 + 10 + máx(consumidores). Con las medidas verificadas se suman los extremos de cada IC (cota conservadora de la media compuesta, no un IC de la suma); el máximo de los consumidores se toma extremo a extremo y un consumidor sin medida cuenta su presupuesto.

| Composición | NCS (alto) | máx(consumidores) (alto) | Total (media) | Total [bajo; alto] | Umbral | Resultado |
|-------------|-----|--------------------|---------------|--------------------|--------|-----------|
| Presupuestos (E2) | 230,0 s | 300,0 s | 780,0 s | [780,0; 780,0] | ≤ 900 s | satisfecha con margen |
| Medidas verificadas | 184,3 s | 300,0 s | 733,8 s | [733,3; 734,3] | ≤ 900 s | satisfecha con margen |
| Medidas verificadas, férreo antes del rediseño (rail-e3) | 184,3 s | 300,0 s | 733,8 s | [733,3; 734,3] | ≤ 900 s | satisfecha con margen |
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

Férreo: su extremo alto (114,1 s) queda 185,9 s por debajo del presupuesto de los demás consumidores (300 s), así que no fija el máximo del grupo; mientras los demás estén en su presupuesto, SoS-QS1 conserva el margen con el férreo hasta 375,7 s y se viola por encima de 465,7 s.
