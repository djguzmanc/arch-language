# Correcciones a la Entrega 3 (feedback del profesor)

Este documento recoge los cambios hechos después de entregar `team-F-p3.pdf`. `INFORME.md` no cambia:
sigue siendo la fuente del informe entregado. `models/sos.arch` y `out/sos/` tampoco cambian.
Marcas en el código: `[F]` es una adaptación propia; `[F, as C]` se alinea con el lenguaje común
(equipo C).

## (a) F-QS7: la caché no entraba en la cadena

**Qué dijo el profesor.** CACHE y F-K38a/b no aparecían en `FQS7CapacityRequest`
(`[RSV | TRN | POS], TRAD`): el efecto de la caché se había metido a mano en el modelo.

**Qué había realmente en el modelo.** El cambio manual fue la `capacity` de reservas-ms: 12 → 40
solicitudes/s en `rail-e2.arch` (A7 de la Entrega 2: reservas-ms atiende 12/s cuando calcula la
capacidad y 40/s cuando lee la capacidad ya calculada). No se cambió ninguna latencia.

**Qué se cambió.**

- Gramática (`arch.tx`): `capacity` en un conector, solo en una dependencia bloqueante, con el
  significado «tasa que el origen logra leyendo por esta dependencia» (distinta del `event_capacity`
  del lenguaje común). Factor nuevo `Q reads S`.
- Semántica (`transformations.py`): `Q reads S` es la cola Q atendiendo mientras lee S de forma
  bloqueante; su tasa de servicio es la `capacity` de la dependencia Q → S, con media
  1/(capacity − load de Q). Cuenta como cola en el reparto de Boole del percentil.
- Restricciones C5 (`metamodel.py`): `capacity` de conector solo en dependencia + bloqueante; en
  `Q reads S`, Q es una cola, existe una dependencia bloqueante Q → S con `capacity` mayor que el
  `load` de Q y un flujo de datos S → Q con la respuesta; `reads` solo en latencia y sin presupuesto.
- Modelo `rail-e2.arch`: RSV vuelve a su valor real `capacity 12 load 8`; F-K38a declara
  `capacity 40`; la cadena es `[RSV reads CACHE | TRN | POS], TRAD` (F-K38b es la respuesta).
  `rail-e1.arch` no cambia (no tiene caché).

| Modelo | Antes | Después |
|--------|-------|---------|
| e1, F-QS7 (p99) | 1400 ms, no cumple | 1400 ms, no cumple (sin cambios) |
| e2, F-QS7 (p99) | 215 ms, cumple (RSV 40/8 escrito a mano) | 215 ms, cumple (RSV 12/8 leyendo CACHE por F-K38a a 40/s) |

La cifra coincide con la de la Entrega 2; ahora sale de la estructura y no de un valor ajustado.

## (b) F-QS2: `latency 1200` precalculado

**Qué dijo el profesor.** F-K11 tenía `latency 1200`, que es 3 × `period 400` calculado a mano;
`period` solo se usaba como booleano (en la lista de suministros silenciosos).

**Qué se cambió.**

- Gramática: métrica `detection` y propiedad `misses` en conectores, como en el lenguaje común.
  Se corrigió el comentario de `period`, que decía que un silencio mayor que un periodo es una falla:
  el receptor detecta el silencio tras `misses` periodos.
- Semántica (como el común): en `detection` un conector aporta period × misses más su `latency` si
  la declara; un componente aporta su `latency`; `= valor` y `= unbounded` como en latencia; un grupo
  cuenta su máximo; sin percentil.
- C5: `misses` necesita `period` y es un entero ≥ 1; en `detection` cada conector necesita
  `period` y `misses` (o un presupuesto) y cada componente `latency` (o un presupuesto); el percentil
  solo aplica a latencia. Diferencia con el común: allí `misses` vale 1 por defecto; aquí es
  obligatorio cuando el conector participa en una detección.
- Modelos: en e2, F-K11 pasa a `period 400 misses 3` (sin `latency`) y F-QS2 usa `detection`. En e1,
  F-QS2 usa `detection` y conserva `F_K11 = unbounded` (F-K11 no tiene cadencia, A11).
- La regla de suministros silenciosos (`_silences`) no cambia.

| Modelo | Antes | Después |
|--------|-------|---------|
| e1, F-QS2 | latencia no acotada, no cumple | detección no acotada, no cumple |
| e2, F-QS2 | latencia 1500 ms (1200 + 300), cumple | detección 1500 ms (3 × 400 + 300), cumple |

## Análisis nuevo: toma de control del SAM (F-QS5)

Con `detection` se puede escribir la toma de control que la Entrega 3 dejó fuera (§7.1): F-K36 es el
latido del SAM principal hacia SAM-B (`SAM -> SAMB`, «Latido cada 0,5 s…»), ahora con
`period 500 misses 3`.

```
analysis FQS5Takeover scenario "F-QS5 (toma de control)" detection target 5000 :
  F_K36, SAMB = 1000
```

Resultado en e2: 3 × 500 ms + 1000 ms de conmutación (presupuesto de SAM-B, A9) = **2500 ms**,
cumple el objetivo de 5000 ms. F-K13b y F-K34b no llevan `misses`.

## Modelos mal formados nuevos (`invalid/`)

| Archivo | Restricción | Mensaje |
|---------|-------------|---------|
| `c5-misses.arch` | `misses` sin `period` | `F_K11: misses needs a period` |
| `c5-detection.arch` | conector sin `period`/`misses` en `detection` | `FQS2SilentConcentrator: F_K11 has no period and misses` |
| `c5-read.arch` | `reads` sin dependencia bloqueante con `capacity` | `FQS7CapacityRequest: RSV reads RSVDB through no blocking dependency that declares capacity` |
| `c5-read-response.arch` | `reads` sin conector de respuesta | `FQS7CapacityRequest: RSV reads RSVDB with no data flow RSVDB -> RSV for the reply` |

Los seis rechazos anteriores conservan su mensaje.
