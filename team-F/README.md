# team-F-p3 — Modelado arquitectónico del Sistema de Transporte Férreo

Entrega 3 del equipo F (Arquitectura de Software a Gran Escala, 2026-II). El informe es
`team-F-p3.pdf`; las adaptaciones, restricciones, convenciones y resultados están explicados allí.

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
| `arch.tx` | Gramática (M2). Las adaptaciones del equipo están marcadas `[F]` |
| `metamodel.py` | Restricciones C1–C7 |
| `transformations.py` | Tabla de conectores, vistas C&C y análisis |
| `generation.py` | Lee cada modelo, verifica que sea conforme y aplica las transformaciones. Sin argumentos procesa todo `models/` |
| `models/sos.arch` | Modelo conjunto, idéntico en las entregas de los seis equipos |
| `models/rail-e1.arch` | Estructura de partida: Entrega 1 con las correcciones CR1–CR4 y las propiedades de la Entrega 2 |
| `models/rail-e2.arch` | Estructura resultante de la Entrega 2 |
| `invalid/` | Modelos mal formados de C5, C6 y C7, y `expected-rejections.txt` con el mensaje de cada uno |
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
