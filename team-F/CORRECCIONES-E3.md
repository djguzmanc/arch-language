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
- Restricciones C5 (`metamodel.py`):
  - `capacity` de conector solo en una dependencia bloqueante con un único link; su fuente es una
    cola con `load` y la `capacity` es mayor que ese `load` (se use o no en un análisis);
  - en `Q reads S`, Q es una cola, hay exactamente una dependencia bloqueante Q → S con `capacity` y
    un flujo de datos S → Q con la respuesta;
  - `reads` solo en latencia y sin presupuesto.
- Modelo `rail-e2.arch`: RSV vuelve a su valor real `capacity 12 load 8`; F-K38a declara
  `capacity 40`; la cadena es `[RSV reads CACHE | TRN | POS], TRAD` (F-K38b es la respuesta).
  En `rail-e1.arch` F-QS7 no cambia: no hay caché y la cadena sigue siendo `RSV, TRN, POS, TRAD`.

| Modelo | Antes | Después |
|--------|-------|---------|
| e1, F-QS7 (p99) | 1400 ms, no cumple | 1400 ms, no cumple (sin cambios) |
| e2, F-QS7 (p99) | 215 ms, cumple (RSV 40/8 escrito a mano) | 215 ms, cumple (RSV 12/8 leyendo CACHE por F-K38a a 40/s) |

La cifra coincide con la de la Entrega 2. La tasa de 40/s sigue siendo un dato de entrada de A7
(Entrega 2); lo que cambia es dónde se declara: en la dependencia de lectura F-K38a y no en RSV. A7
da dos tasas medidas (12/s calculando la capacidad, 40/s leyendo la ya calculada), así que la tasa es
una propiedad del camino de lectura, no del servicio. F-K39 actualiza la caché tras cada reserva o
cambio de surco; por eso se asume que la lectura siempre acierta y no se modela una tasa de fallos
de caché (limitación declarada; candidata a un análisis de sensibilidad en la Entrega 4).

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
- C5: `misses` necesita `period`. La gramática lo restringe a un entero ≥ 1 (`/[1-9][0-9]*/`), así
  que `misses 0` o `misses 1.5` son errores de sintaxis; todo valor aceptado es también un `NUMBER`
  válido para el `misses` del común. En `detection` cada conector necesita
  `period` y `misses` (o un presupuesto) y cada componente `latency` (o un presupuesto); el percentil
  solo aplica a latencia. Diferencia con el común: allí `misses` vale 1 por defecto; aquí es
  obligatorio cuando el conector participa en una detección.
- Modelos: en e2, F-K11 pasa a `period 400 misses 3` (sin `latency`) y F-QS2 usa `detection`. En e1,
  F-QS2 usa `detection` y conserva `F_K11 = unbounded`: en e1 F-K11 no tiene `period` (A11) y, sin
  cadencia, no hay detección derivable.
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

Resultado en e2: **2500 ms**, que cumple el objetivo de 5000 ms y replica la cifra de la Entrega 2
(F-QS5): «3 latidos × 0,5 s + 1 s de conmutación (cota de A9) = 2,5 s ≤ 5 s». En esta métrica el
presupuesto `SAMB = 1000` no es una detección: representa la conmutación de SAM-B después de detectar
el silencio del latido. F-K13b y F-K34b no llevan `misses`.

## Modelos mal formados nuevos (`invalid/`)

| Archivo | Restricción | Mensaje |
|---------|-------------|---------|
| `c5-misses.arch` | `misses` sin `period` | `F_K11: misses needs a period` |
| `c5-misses-zero.arch` | `misses 0` (error de sintaxis de textX) | `Expected Misses` |
| `c5-detection.arch` | conector sin `period`/`misses` en `detection` | `FQS2SilentConcentrator: F_K11 needs period and misses (or a budget)` |
| `c5-read.arch` | `reads` sin dependencia bloqueante con `capacity` | `FQS7CapacityRequest: RSV reads RSVDB through no blocking dependency that declares capacity` |
| `c5-read-response.arch` | `reads` sin conector de respuesta | `FQS7CapacityRequest: RSV reads RSVDB with no data flow RSVDB -> RSV for the reply` |
| `c5-read-several.arch` | dos dependencias Q → S con `capacity` | `FQS7CapacityRequest: RSV reads RSVDB: several dependencies with capacity ['F_K22x', 'F_K22y']` |

Los seis rechazos anteriores a estas correcciones conservan su mensaje.

## Limitaciones conocidas

- `beta` de un grupo solo se usa en disponibilidad; en latencia y detección se ignora sin aviso.
- No se rechaza que un mismo análisis use la misma cola leyendo (`RSV reads CACHE`) y sin leer
  (`RSV`) a la vez.
- Se asume acierto de caché siempre (ver (a)); no hay tasa de fallos.
