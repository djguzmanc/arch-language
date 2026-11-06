# team-F-p3 — Modelado arquitectónico del Sistema de Transporte Férreo

Entrega 3 del equipo F (Arquitectura de Software a Gran Escala, 2026-II). Contiene:

- el lenguaje del Laboratorio 4 adaptado al férreo;
- el modelo conjunto `sos.arch`;
- los modelos del férreo antes (`rail-e1.arch`) y después (`rail-e2.arch`) de la Entrega 2;
- las transformaciones, los artefactos generados y el borrador del informe.

Este README es el documento de traspaso: cuenta qué se hizo, por qué y qué falta.
El detalle técnico (tablas de adaptaciones, restricciones, convenciones y resultados) está en
`INFORME.md`, para no repetirlo y que no se desincronice.

---

## 1. Estado

| Pieza que pide el enunciado (§4.2) | Estado | Dónde |
|------------------------------------|--------|-------|
| Lenguaje: gramática y restricciones con las adaptaciones del equipo | Hecho | `arch.tx`, `metamodel.py` |
| Modelos: `sos.arch` y los dos del constituyente | Hecho | `models/` |
| Transformaciones, programa de generación y Dockerfile | Hecho | `transformations.py`, `generation.py`, `Dockerfile` |
| Artefactos generados de cada modelo | Hecho | `out/` |
| Un modelo mal formado por cada restricción agregada | Hecho | `invalid/` |
| Informe (.pdf) | Borrador listo. Faltan las figuras y convertirlo | `INFORME.md` (sección 6 de este README) |
| `.zip` `team-F-p3` subido a Classroom por una sola persona | Falta | Fecha límite: viernes 6 de noviembre de 2026, 23:59 |

Verificado con Python y textX 4.3.0, la misma versión del Dockerfile:

- los tres modelos se aceptan;
- los cuatro modelos mal formados se rechazan con el mensaje esperado;
- `out/sos/` es idéntico al del repo conjunto (`diff -r`).

---

## 2. Cómo correrlo

```bash
docker build -t lssa-team-f .
docker run --rm -v "$PWD:/app" lssa-team-f                           # procesa los tres modelos de models/
docker run --rm -v "$PWD:/app" lssa-team-f invalid/c6-hierarchy.arch  # un modelo mal formado: debe salir REJECTED
```

Sin Docker:

```bash
python3 -m venv .venv && .venv/bin/pip install textX==4.3.0
.venv/bin/python generation.py
```

Los artefactos quedan en `out/<modelo>/`:

- `connectors.md`: la tabla de conectores.
- `view.mmd`: la vista C&C completa. Si el modelo tiene traductor, también `view-operation.mmd` y `view-coordination.mmd`. Todas son Mermaid y se pueden pegar en mermaid.live.
- `analysis.md`: el análisis.

Si se cambia `models/rail-e1.arch`, hay que regenerar los modelos mal formados, que son copias suyas
con un solo cambio:

```bash
python tools/make_invalid.py
for f in invalid/*.arch; do python generation.py $f; done > invalid/expected-rejections.txt
```

Si cambia un modelo, también hay que actualizar a mano las cifras de `INFORME.md`, §6, y sus anexos.

---

## 3. Archivos

| Archivo | Contenido |
|---------|-----------|
| `arch.tx` | Gramática (M2). Las adaptaciones del equipo están marcadas `[F]` |
| `metamodel.py` | Restricciones C1–C7 |
| `transformations.py` | Tabla de conectores, vistas C&C y análisis |
| `generation.py` | Lee cada modelo, verifica que sea conforme y aplica las transformaciones. Sin argumentos procesa todo `models/` |
| `models/sos.arch` | Modelo conjunto, copiado sin cambios del repo conjunto |
| `models/rail-e1.arch` | Estructura de partida: la Entrega 1 con las correcciones CR1–CR4 y las propiedades de la Entrega 2 |
| `models/rail-e2.arch` | Estructura resultante de la Entrega 2 |
| `invalid/` | Cuatro modelos mal formados y `expected-rejections.txt` con el mensaje de cada uno |
| `tools/make_invalid.py` | Genera los modelos de `invalid/` a partir de `rail-e1.arch` |
| `out/` | Artefactos generados |
| `INFORME.md` | Borrador del informe, con la estructura que pide el enunciado |

---

## 4. Contexto

**El repo conjunto.** `fabioalvarez/arch-language` tiene el trabajo del equipo D (Coordinación
Nacional): su lenguaje, sus modelos, su informe y el `sos.arch` conjunto. Nuestra cuenta solo tiene
permiso de lectura ahí.

**Por qué esta carpeta va aparte.** El enunciado no pide subir el trabajo al repo conjunto: cada
equipo entrega su propio `.zip`. Lo único que debe ser idéntico entre equipos es `sos.arch` y su
análisis de SoS-QS1 (§4.1). Esta carpeta es autocontenida y se puede mover a un repo propio.

**Acuerdo tomado como final.** Es la versión v4 del documento conjunto, dando por aceptado lo que
decía [CONFIRMAR], porque el documento estaba así desde la semana anterior. `sos.arch` coincide con esa
versión: los 36 conectores, los presupuestos de M4 y el resultado de 780 s. Si alguien cambia
`sos.arch` en el repo conjunto, hay que copiarlo de nuevo aquí y regenerar.

**Por qué no se mandó un mensaje a los equipos.** Se redactó uno, pero ninguno de sus puntos era
necesario para avanzar: que `sos.arch` corra con nuestro lenguaje depende solo de nosotros, y las
convenciones de nombres ya vienen en `sos.arch`.

**Por qué no se reusó el lenguaje del equipo D.** Sus adaptaciones (`domain`, `deadline`,
`recovery`) sirven a sus escenarios. Los nuestros necesitan colas y percentiles. De D se tomó una sola
idea: el presupuesto escrito en el análisis (`= valor`).

---

## 5. Decisiones y su razón

Cada decisión está explicada en `INFORME.md`. Aquí van las que no son obvias:

- **Todas las adaptaciones del lenguaje son opcionales**, para que `sos.arch`, escrito en el lenguaje
  base, dé el mismo resultado (INFORME, §4).
- **C6 (jerárquico) es la restricción de estilo.** Rechaza el modelo ERTMS del Laboratorio 4, porque
  allí la unidad a bordo tiene dos autoridades legítimas (MAS y STM). Es a propósito: la regla es del
  estilo jerárquico del férreo, no del SoS (INFORME, §4.3).
- **El Rail Gateway no lleva propiedades**, igual que en `sos.arch`. Sus tiempos los llevan el
  Traductor y F-K19 (convención 3).
- **`unbounded` existe** para escribir el «antes» de F-QS2 y SoS-QS1, donde la Entrega 1 no acota el
  tramo. Así el modelo dice «no acotado» en vez de inventar una cifra o dejar el análisis fuera
  (convenciones 9 y 12).
- **«F-QS5 con vía» se agregó** por la retroalimentación del profe. Usa las cifras de la Entrega 2,
  §8.3. No se duplicaron el concentrador ni el enclavamiento en `rail-e2`, porque eso ya no sería el
  «después» de la Entrega 2 (INFORME, §7.3).
- **`period` y la lista de silencios** responden a la recomendación sobre F-K7. No se agregó un latido
  en `rail-e2` por la misma razón.
- **Las vistas de operación y de coordinación** responden a «desenredar el Traductor».
- **Los acoplamientos de los conectores globales se copiaron de `sos.arch`**, aunque la Entrega 2
  clasificó tres de ellos distinto desde el lado del férreo (convención 11).

---

## 6. Pendientes

**En esta entrega:**

1. **Figuras.** Ya están renderizadas en `figures/` (SVG y PNG) y las dos vistas parciales de
   `rail-e2` están en el informe (§4.4). Si un modelo cambia, hay que regenerarlas. mermaid-cli usa
   el Chrome instalado en lugar de descargar Chromium, y `puppeteer.json` es
   `{"executablePath": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"}`:
   ```bash
   export PUPPETEER_SKIP_DOWNLOAD=true
   npx -y @mermaid-js/mermaid-cli@11.4.2 -p puppeteer.json -i out/rail-e2/view-operation.mmd \
       -o figures/rail-e2-view-operation.svg -b white
   ```
   La vista de operación queda densa: unos 50 conectores. Si se ve pesada en el PDF, se puede usar la
   figura draw.io de la Entrega 2 como figura principal y dejar la de Mermaid como evidencia generada.
2. **Probar Docker.** Todo se verificó con Python y textX 4.3.0, pero esta máquina no tenía Docker.
   Correr los dos comandos de la sección 2.
3. **Convertir `INFORME.md` a PDF y armar el `.zip`** con esta carpeta: código, modelos, `invalid/`,
   `out/` y el PDF. Sin `.venv` ni `__pycache__`.

**Fuera de esta entrega (requieren a otros equipos o a la siguiente entrega):**

4. **Texto común de la sección 3.** El enunciado (§4.1) pide `sos.arch` y su análisis idénticos en
   todas las entregas. Eso se cumple, pero la prosa de la §3 la redactamos nosotros. Si los equipos
   acuerdan un texto común, hay que reemplazarlo.
5. **Presupuesto de red de F-QS7**, como máximo 585 ms ida y vuelta. Requiere un acuerdo bilateral con
   los puertos y Carretera (SoS-K3, SoS-K7 y SoS-K24).
6. **Latido o sondeo en F-K7/F-K37, política de telemetría, y duplicar concentrador y enclavamiento.**
   Son recomendaciones de diseño del profe para la siguiente entrega. El modelo ya muestra el efecto:
   - F-K7 y F-K37 aparecen en la lista de silencios.
   - «F-QS5 con vía» no cumple. Según el cálculo de la revisión, duplicar los dos con β = 0,1 lo
     llevaría a ≈ 99,96 %.
7. **Silencios residuales que la Entrega 2 no trata.** Son F-K9 y F-K10 (equipos de campo → 
   concentrador) y F-K14 y F-K35 (sensores → unidad a bordo). La comparación de sensores detecta si
   divergen, pero no si los dos callan a la vez.

---

## 7. Revisiones hechas

**Primera revisión independiente.** Corrigió:

- C7, que aceptaba saltarse el traductor y daba mensajes falsos;
- los grupos de disponibilidad, que usaban solo la primera réplica;
- `load 0`, que se rechazaba;
- el error de C6, que señalaba el conector equivocado;
- los 0,3 s del enclavamiento, que faltaban en `rail-e1`;
- F-K23b, que no reflejaba su cambio;
- SoS-QS1, que faltaba en `rail-e1`;
- la convención del SAM activo, que no estaba documentada.

**Segunda revisión, con tres revisores en paralelo** (consistencia con las Entregas 1 y 2 y el
Laboratorio 4, retroalimentación del profe, y un adversario del lenguaje). Corrigió:

- **SoS-QS1 en `rail-e1`:** reportaba «780 s, cumple», cuando el férreo no tenía reconciliación
  definida. Ahora sale «no acotado», con `unbounded`.
- **F-QS2:** ya se puede escribir en el «antes» (no acotado).
- **Retroalimentación del profe:** se agregaron «F-QS5 con vía», `period` con la lista de silencios,
  las vistas por responsabilidad, las aristas sin duplicar y la sección 7.3 del informe.
- **Los 10 elementos modificados** se marcan en `rail-e2`, y se declara cuáles cambian solo de
  comportamiento.
- **C5:** se rechazan un presupuesto en disponibilidad y una cola con latencia fija, y se corrigió un
  mensaje engañoso.
- **Documentación:** el alcance de C6 frente al ERTMS, el texto de SoS-K18a/b, F-K25a/b, la
  cola de telemetría, la red de F-QS7 y los encabezados de los modelos.

Después de cada revisión, las cifras de la Entrega 2 siguieron reproduciéndose.
