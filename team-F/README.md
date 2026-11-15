# team-F-p3 — Modelado arquitectónico del Sistema de Transporte Férreo

Entrega 3 del equipo F (Arquitectura de Software a Gran Escala, 2026-II). El informe es
`team-F-p3.pdf`; las adaptaciones, restricciones, convenciones y resultados están explicados allí.
Las correcciones posteriores al feedback de la Entrega 3 (métrica `detection`, propiedad `misses`,
lectura `Q reads S`) están en `CORRECCIONES-E3.md`; el informe no las incluye.

La Entrega 4 (verificación) está en la sección [Entrega 4 — Verificación](#entrega-4--verificación).

## Ejecución

```bash
docker build -t lssa-team-f .
docker run --rm -v "$PWD:/app" lssa-team-f                            # procesa los tres modelos de models/
docker run --rm -v "$PWD:/app" lssa-team-f invalid/c6-hierarchy.arch  # un modelo mal formado: sale REJECTED
```

Sin Docker:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python generation.py
```

Los artefactos quedan en `out/<modelo>/`:

- `connectors.md`: la tabla de conectores.
- `view.mmd`: la vista C&C en Mermaid. Si el modelo tiene traductor, también `view-operation.mmd` y `view-coordination.mmd`.
- `analysis.md`: el análisis de los escenarios.

## Archivos

| Archivo | Contenido |
|---------|-----------|
| `arch.tx` | Gramática (M2). Las adaptaciones del equipo están marcadas `[F]`; las alineadas con el lenguaje común, `[F, como C]` (en el código, `[F, as C]`) |
| `metamodel.py` | Restricciones C1–C7 y, desde la Entrega 4, C12–C15. C5 incluye `misses`, `detection`, `capacity` de conector, `Q reads S` y las reglas de la Entrega 4 (`hit`, `reads` y colas en un path, `drain`). El encabezado tiene la tabla de equivalencias con la numeración del lenguaje común |
| `transformations.py` | Tabla de conectores, vistas C&C y análisis |
| `generation.py` | Lee cada modelo, verifica que sea conforme y aplica las transformaciones. Sin argumentos procesa todo `models/` |
| `models/sos.arch` | Modelo conjunto, idéntico en las entregas de los seis equipos |
| `models/rail-e1.arch` | Estructura de partida: Entrega 1 con las correcciones CR1–CR4 y las propiedades de la Entrega 2 |
| `models/rail-e2.arch` | Estructura resultante de la Entrega 2 |
| `invalid/` | Modelos mal formados de C5 (`c5-queue-load`, `c5-percentile`, `c5-misses`, `c5-detection`, `c5-misses-zero`, `c5-read`, `c5-read-response`, `c5-read-several` y, de la Entrega 4, los de la tabla de restricciones de abajo), C6, C7, C12–C15, y `expected-rejections.txt` con el mensaje de cada uno |
| `CORRECCIONES-E3.md` | Correcciones al feedback de la Entrega 3, con las cifras antes y después |
| `out/` | Artefactos generados |
| `figures/` | Vistas renderizadas desde los `.mmd`, en SVG y PNG |
| `INFORME.md` | Fuente del informe |
| `tools/make_invalid.py` | Genera los modelos de `invalid/` a partir de `rail-e1.arch` |
| `tools/build_report.py` | Genera `team-F-p3.pdf` a partir de `INFORME.md` |
| `tools/mermaid-config.json` | Configuración con la que se renderizan las figuras |

## Regenerar

Si cambia `models/rail-e1.arch`, hay que regenerar los modelos mal formados:

```bash
.venv/bin/python tools/make_invalid.py
for f in invalid/*.arch; do .venv/bin/python generation.py "$f"; done > invalid/expected-rejections.txt
```

Si cambia un modelo, también hay que actualizar a mano las cifras de `INFORME.md` (§6 y anexos) y volver a
renderizar las figuras:

```bash
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD:/data" minlag/mermaid-cli:11.4.2 \
  -c tools/mermaid-config.json -i out/rail-e2/view-operation.mmd \
  -o figures/rail-e2-view-operation.svg -b white -w 3200 -s 2
```

El mismo comando con extensión `.png` genera la imagen. `tools/mermaid-config.json` usa el motor de
distribución ELK, que mantiene cada rótulo sobre su línea.

Para generar el PDF hace falta Google Chrome (o indicar otro navegador con la variable `CHROME`):

```bash
.venv/bin/pip install -r tools/requirements-report.txt
.venv/bin/python tools/build_report.py
```

## Entrega 4 — Verificación

La verificación sigue el Laboratorio 5 y el lenguaje común de la Entrega 4 (equipo D). Cada modelo
de iteración (`models/rail-e1.arch` … `models/rail-e4.arch`) produce `out/<modelo>/graph.png` y
`out/<modelo>/verification.md`. La simulación usa semillas 1..n por réplica, así que dos corridas
dan los mismos archivos byte a byte. Los artefactos de la Entrega 3 (`analysis.md`,
`connectors.md`, `view*.mmd`) no cambian con las extensiones del lenguaje.

### Ejecución

```bash
docker build -f Dockerfile.verification -t lssa-team-f-verif .

# Verificación de cada modelo (grafo, propiedades estructurales, simulación, reporte)
docker run --rm -v "$PWD:/app" lssa-team-f-verif models/rail-e1.arch   # iteración 1
docker run --rm -v "$PWD:/app" lssa-team-f-verif models/rail-e2.arch   # iteración 2
docker run --rm -v "$PWD:/app" lssa-team-f-verif models/rail-e3.arch   # iteración 3
docker run --rm -v "$PWD:/app" lssa-team-f-verif models/rail-e4.arch   # iteración 4

# C16: correspondencia de cada modelo con sos.arch (nuestros modelos dicen `system Rail`;
# --as RLS los compara como el constituyente RLS). Sale con estado 1 si alguno no corresponde.
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-f-verif \
  correspondence.py --as RLS models/sos.arch models/rail-e1.arch models/rail-e2.arch \
  models/rail-e3.arch models/rail-e4.arch

# P11: SoS-QS1 (M4) bottom-up, top-down y sensibilidad -> out/sos/sos-qs1.md
# (después de verificar rail-e3 y rail-e4: lee su marcador RLS_RECONCILIATION_S)
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-f-verif sos_compose.py

# Contribución de cada táctica y sensibilidad (iteración 4)
docker run --rm -v "$PWD:/app" --entrypoint python lssa-team-f-verif tactics_check.py
```

Sin Docker:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-verification.txt
.venv/bin/python verification.py models/rail-e2.arch
.venv/bin/python correspondence.py --as RLS models/sos.arch models/rail-e*.arch
.venv/bin/python sos_compose.py                          # o --rail MEDIA BAJO ALTO a mano
.venv/bin/python tactics_check.py
```

Determinismo: correr dos veces y comparar.

```bash
for m in models/rail-e*.arch; do .venv/bin/python verification.py "$m"; done
cp -r out /tmp/out-1
for m in models/rail-e*.arch; do .venv/bin/python verification.py "$m"; done
diff -r /tmp/out-1 out && echo "idénticas"
```

No regresión del lenguaje (deben salir vacíos o iguales):

```bash
.venv/bin/python generation.py && git diff --stat out/        # artefactos de la Entrega 3 idénticos
for f in invalid/*.arch; do .venv/bin/python generation.py "$f"; done | diff - invalid/expected-rejections.txt
```

`sos_compose.py` toma la medida del férreo de la arquitectura final, `out/rail-e4/verification.md`
(con T4.3), de una línea `RLS_RECONCILIATION_S <media> <bajo> <alto>` (segundos, punto decimal; el
drain de F-QS1 con los parámetros nominales), y muestra como evolución la de
`out/rail-e3/verification.md` (antes del rediseño). La del NCS es la del acuerdo conjunto,
sección 1.3.3 (ncs-e4 del equipo D: 183,8 s, IC [183,3; 184,3]; `--ncs` la cambia). Los tramos sin
medida cuentan su presupuesto. El reporte declara tres cosas:

- el repositorio del equipo D publica para ncs-e4 184,9 s [183,8; 186,1]; la diferencia no cambia
  ninguna conclusión y debe resolverse en el acuerdo;
- T4.3 supone que SoS-K18a devuelve todas las unidades de un camión en una consulta (por confirmar
  en el acuerdo; si no, la cifra de rail-e3 es la conservadora);
- se compone nuestro `drain` con el `recovery` de D, que además cuenta la espera 1/λ de la primera
  llegada (0,67 s según D).

Resultado actual (`out/sos/sos-qs1.md`): férreo 108,5 s [102,9; 114,1] en rail-e4 (144,9 s
[140,7; 149,2] en rail-e3), con margen frente a 300 s; composición con las medidas verificadas
733,8 s [733,3; 734,3] ≤ 900 s, con margen (el máximo de los consumidores sigue en el presupuesto
de 300 s de los demás). Holgura hasta violar: 165,7 s (Carretera hasta 365,7 s, NCS hasta 350 s,
consumidores hasta 465,7 s). Con el NCS sin su rediseño (ncs-e2 de D) SoS-QS1 se viola.

C16 (`correspondence.py --as RLS`): rail-e2, rail-e3 y rail-e4 corresponden con `sos.arch`;
rail-e1 solo falla en `K3: global connector SoS_K34 of the joint model is missing` (SoS-K34 lo
agregó el acuerdo v4 después de la estructura de partida).

### Extensiones del lenguaje

Marcas en `arch.tx`: [L5] Laboratorio 5, [D4] lenguaje común de la Entrega 4 (equipo D), [F] equipo F.

| Extensión | Marca | Sintaxis | Semántica |
|-----------|-------|----------|-----------|
| `scenarios`, `tactics` en el modelo | [L5, D4] | después de los `analysis` | — |
| `store` de componente | [L5, D4] | `component ARRDB … store` | Retiene los trabajos mientras el siguiente componente está caído; [D4] un store caído retiene lo que recibe |
| `capacity` de componente | [F] (E3) = [L5] | `… capacity 12 load 8` | Tasa de servicio de una cola FIFO (exponencial en la simulación) |
| `load` de componente | [F] (E3) | `… load 8` | Solo para el análisis analítico de la Entrega 3; la simulación toma las llegadas de los `workload` |
| `hit` de conector | [F] | `connector F_K38a … capacity 40 hit 0.9` | Fracción en (0, 1] de las lecturas servidas a la `capacity` del conector (aciertos de caché); el resto, a la de la cola. Sin `hit`: 1 (supuesto de la Entrega 3) |
| Escenario con seis partes | [D4] | `scenario X "F-QS7" attribute … source … stimulus … artifact A, B environment … response …` | `artifact` refiere elementos del modelo |
| `verified_by`, `not_verifiable` | [D4] | `verified_by FQS7CapacityRequest` / `not_verifiable "lo que falta"` | La medida se verifica con un análisis del modelo, o se declara no verificable con el concepto que falta |
| `workload` | [L5] | `workload W rate 8 : A -> B -> C` | Llegadas de Poisson que siguen el path |
| `parallel` de conector | [F] | `connector F_K23a nature dependency coupling blocking parallel` | Dependencia bloqueante cuyos links (≥ 2, del mismo origen) se llaman a la vez: el paralelismo queda en la estructura, no solo en el workload |
| Fork/join en el path | [F] | `LGW -> TRAD -> [RSV reads CACHE \| TRN \| POS]` | Las ramas corren en paralelo; el trabajo sigue cuando termina la más lenta. Entra por un conector `parallel` |
| `Q reads S` en el path | [F] | `RSV reads CACHE` | La cola Q lee S por su dependencia bloqueante con `capacity`, a la fracción `hit` |
| `compact` | [D4] | `workload W rate r compact n : …` | Mientras un store retiene el workload, solo se guardan los últimos n |
| `fault` | [L5] | `fault ARR down at 0 for 14400` | Intervalo sin servicio; los trabajos se pierden salvo que un store los retenga |
| `vary` | [L5] | `vary ARR : 1.667, 1.25` / `vary Requests : …` | Varía la `capacity` de un componente o la `rate` de un workload |
| `vary hit` | [F] | `vary hit F_K38a : 1, 0.9, 0.5, 0` | Varía la fracción `hit` de un conector con `capacity` (valores en [0, 1]) |
| `measure` | [L5, D4] | `measure p99_latency W <= 800 ms`, `lost`, `recovery` | Como en el Laboratorio 5 (`recovery` como en D) |
| `measure drain` | [F] | `measure drain Units <= 300 s` | Desde el fin de la falla hasta que sale de su path el último trabajo que retuvo un store. A diferencia de `recovery`, no espera la primera llegada posterior (≈ 1/rate) |
| `run` | [L5] | `run 1800 warmup 60 replications 10` | Duración, calentamiento (s) y réplicas (semillas 1..n) |
| `tactic` | [D4] | `tactic T "…" for QS_F7 introduces CACHE, F_K38a changes RSV` | Táctica ligada al escenario que la motiva y a los elementos que introduce o cambia |

### Restricciones de la Entrega 4

C12–C16 tienen la numeración del lenguaje común. Nuestras C6 (jerárquico) y C7 (gateway + ACL) se
conservan; en el lenguaje común C6 y C7 son otras reglas (tabla de equivalencias al comienzo de
`metamodel.py`).

| Restricción | Contenido | Modelo rechazado | Mensaje |
|-------------|-----------|------------------|---------|
| C12 [L5 C6, F] | Cada salto de un workload sigue un conector (en cualquier sentido); en un fork, cada par (paso anterior, rama) y (rama, paso siguiente) | `c12-hop.arch` | `X12: X12Jobs goes from RSV to LGW without a connector` |
| C13 [L5 C7] | Una falla solo en un componente con `capacity` | `c13-fault.arch` | `X13: fault on TRAD, which has no capacity` |
| C14 [D4] | Un escenario de calidad tiene sus seis partes, y su medida se simula (workloads, measures y run), se verifica con `verified_by` o se declara `not_verifiable` | `c14-parts.arch`, `c14-run.arch` | `X14: quality scenario without environment`; `X14R: a simulated scenario needs at least one measure and its run` |
| C14 [F] | Un escenario simulado tiene al menos 2 réplicas (para el IC) | `c14-replications.arch` | `X14N: a simulated scenario needs at least 2 replications for its confidence interval` |
| C14 [F] | El calentamiento es menor que la duración de la corrida | `c14-warmup.arch` | `X14W: warmup 600 s is not below the run duration 600 s` |
| C15 [D4] | Una táctica introduce o cambia elementos y la motiva un escenario verificado | `c15-tactic.arch` | `X15T: motivated by X15, whose measure is not verified` |
| C16 [D4] | Correspondencia con `sos.arch` (K1–K3): `correspondence.py --as RLS` | — (lo verifica el programa) | `rail-e1`: `K3: global connector SoS_K34 of the joint model is missing` |
| C5 [F] `hit` | `hit` solo en un conector con `capacity` | `c5-hit-capacity.arch` | `F_K22: hit applies only to a connector with capacity` |
| C5 [F] `hit` | `hit` ∈ (0, 1] | `c5-hit-range.arch` | `F_K22x: hit 0 is not in (0, 1]` |
| C5 [F] `vary hit` | Solo sobre un conector con `capacity`, valores en [0, 1] | `c5-vary-hit.arch` | `X5V: vary hit on F_K22, which is not a connector with capacity` |
| C5 [F] `reads` | En un path, `Q reads S` solo sobre una cola con su dependencia de lectura (como en un análisis) | `c5-reads-queue.arch` | `X5R: X5RJobs: TRN reads TRNDB: TRN is not a queue` |
| C5 [F] cola | Una cola aparece una vez por path | `c5-queue-twice.arch` | `X5Q: X5QJobs goes through the queue RSV more than once` |
| C5 [F] `drain` | `drain` exige un `store` en el path de su workload | `c5-drain-store.arch` | `X5D: drain on X5DJobs, whose path has no store` |
| C5 [F] `drain` | `drain` exige una falla en el escenario | `c5-drain-fault.arch` | `X5F: drain needs a fault in the scenario` |
| C5 [F] `drain` | El `store` está en el path antes del componente que falla (o es ese componente): uno después no retiene nada | `c5-drain-order.arch` | `X5O: drain on X5OJobs: no store at or before the failing component (RSV) in its path, so no job is held` |
| C5 [F] `parallel` | Solo en una dependencia bloqueante | `c5-parallel-kind.arch` | `F_K23b: parallel applies only to a blocking dependency` |
| C5 [F] `parallel` | Al menos dos links | `c5-parallel-links.arch` | `F_K3: a parallel connector needs at least two links, it has 1` |
| C5 [F] `parallel` | Todos los links salen del mismo origen | `c5-parallel-source.arch` | `F_K22: the links of a parallel connector leave one source, not ['CRG', 'POS', 'RSV', 'TRN']` |
| C5 [F] fork | Todo fork entra por un conector `parallel` con un link del paso anterior a cada rama | `c5-fork-parallel.arch` | `X5P: X5PJobs: the fork [RSV \| TRN \| POS] after TRAD is not entered through a parallel connector with a link to each branch` |
| C5 [F] fork | Un workload no recorre en secuencia dos o más destinos de un conector `parallel` (eso es un fork) | `c5-parallel-sequence.arch` | `X5S: X5SJobs visits RSV, CRG, targets of the parallel connector F_K2p, in sequence; they are a fork` |

Los modelos de `invalid/` se generan con `tools/make_invalid.py` a partir de `rail-e1.arch`; los
escenarios y tácticas de los casos de la Entrega 4 están escritos en ese script (nombres `X…`).
En `rail-e1` (estructura de partida) F-K23a no es `parallel` y F-QS7 recorre los tres servicios en
secuencia; los casos con fork usan un conector `parallel` propio (`F_K2p`, de la consola de
terminal).

### Archivos de la Entrega 4

| Archivo | Contenido |
|---------|-----------|
| `Dockerfile.verification`, `requirements-verification.txt` | Imagen de verificación: python:3.11-slim, textX 4.3.0, Arpeggio 2.0.3, networkx 3.4.2, matplotlib 3.9.2 |
| `verification.py`, `simulation.py` | Verificación por modelo y simulador de eventos discretos (Laboratorio 5, adaptado del equipo D) |
| `tactics_check.py` | Contribución de cada táctica y sensibilidad |
| `correspondence.py` | C16, copiado del lenguaje común con la opción `--as` |
| `sos_compose.py` | P11: SoS-QS1 (M4) bottom-up, top-down y sensibilidad a parámetros de otros dueños |
| `models/rail-e3.arch`, `models/rail-e4.arch` | Iteraciones 3 (parámetros de F-QS1, estructura de e2) y 4 (rediseño) |
