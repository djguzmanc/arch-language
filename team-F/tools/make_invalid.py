"""Writes the ill-formed models of invalid/ from models/rail-e1.arch, one change each.

A change is a replacement (old, new) of a text that appears once in rail-e1.arch, or a block
inserted with SCENARIO or TACTIC (Delivery 4): a scenario goes before the first tactic of the
model (or at its end) and a tactic at the end, as the grammar orders them. The scenarios and
tactics of these cases are written here, with names X..., so they do not depend on the scenarios
that rail-e1.arch declares.

Run it from team-F/ whenever rail-e1.arch changes, then regenerate the expected messages:
    python tools/make_invalid.py
    for f in invalid/*.arch; do python generation.py $f; done > invalid/expected-rejections.txt
"""
import os
import re

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SCENARIO, TACTIC = 'SCENARIO', 'TACTIC'

# A valid read through a dependency with capacity (C5): reservas-ms reads reservas-db at 40/s.
READ = ('connector F_K22x nature dependency coupling blocking\n'
        '  carries "Lectura de la capacidad ya calculada"\n'
        '  capacity 40{hit}\n'
        '  : RSV -> RSVDB\n'
        'connector F_K22z nature data_flow coupling blocking\n'
        '  carries "Capacidad calculada (respuesta)"\n'
        '  : RSVDB -> RSV\n\n')
GLOBAL = '// Global connectors of the Rail Gateway (as in sos.arch)\n'

# A simulated scenario around the capacity request of F-QS7 (Delivery 4); {path}, {extra} and
# {measure} change per case.
SIMULATED = ('scenario {name} "{label}"\n'
             '  workload {name}Jobs rate 8 : {path}\n'
             '{extra}'
             '  measure {measure}\n'
             '  run {run}\n')
REQUEST = 'LGW -> TRAD -> RSV -> TRAD -> LGW'


RUN = '600 warmup 60 replications 2'

# [F] A parallel connector for the cases with a fork (C5: a fork enters through one). It is not
# F-K23a: rail-e1 visits reservas-ms, trenes-ms and posicion-ms in sequence (F-QS7 before the
# parallelism of Delivery 2), which C5 rejects once F-K23a is parallel. The terminal console
# calls two services at once instead; no workload of rail-e1 visits both in sequence.
def parallel(name, first, second):
    return (GLOBAL,
            f'connector {name} nature dependency coupling blocking parallel\n'
            f'  carries "Consultas simultáneas de la consola de terminal"\n'
            f'  : CTF -> {first}, CTF -> {second}\n\n' + GLOBAL)


FORK = 'LGW -> TRAD -> [RSV | TRN | POS] -> TRAD -> LGW'


def simulated(name, label, comment, path=REQUEST, extra='', measure=None, run=RUN):
    return (SCENARIO, f'// Ill-formed ({label}): {comment}\n' + SIMULATED.format(
        name=name, label=label, path=path, extra=extra, run=run,
        measure=measure or f'p99_latency {name}Jobs <= 800 ms'))


def mark(connector, old_line):
    """Adds parallel to the first line of a connector of rail-e1, with a comment."""
    return (old_line, f'// Ill-formed (C5): {connector}\n' + old_line.rstrip('\n') + ' parallel\n')

CASES = {
    # C6: a second source of control commands over the interlocking.
    'c6-hierarchy.arch': (
        'connector F_K1 nature dependency coupling blocking\n'
        '  carries "Órdenes de planificación y despacho, y consultas de estado"\n'
        '  : CCF -> PLN',
        'connector F_K1 nature dependency coupling blocking\n'
        '  carries "Órdenes de planificación y despacho, y consultas de estado"\n'
        '  : CCF -> PLN\n'
        '// Ill-formed (C6): the console orders routes directly, bypassing planning and dispatch\n'
        'connector F_K1x nature control_command coupling blocking\n'
        '  carries "Solicitudes de ruta desde la consola"\n'
        '  : CCF -> ILK'),
    # C6: the interlocking commands planning, against the flow of authority.
    'c6-cycle.arch': (
        'connector F_K1 nature dependency coupling blocking\n'
        '  carries "Órdenes de planificación y despacho, y consultas de estado"\n'
        '  : CCF -> PLN',
        'connector F_K1 nature dependency coupling blocking\n'
        '  carries "Órdenes de planificación y despacho, y consultas de estado"\n'
        '  : CCF -> PLN\n'
        '// Ill-formed (C6): the interlocking orders planning, which already commands it (F-K5)\n'
        'connector F_K6x nature control_command coupling blocking\n'
        '  carries "Órdenes del enclavamiento a planificación"\n'
        '  : ILK -> PLN'),
    # C7: the translator skips the gateway and crosses the boundary itself.
    'c7-boundary.arch': (
        '// Global connectors of the Rail Gateway (as in sos.arch)\n',
        '// Ill-formed (C7): the translator publishes directly to another constituent\n'
        'connector F_K21x nature event_notification coupling sink\n'
        '  carries "Eventos canónicos publicados sin pasar por el gateway"\n'
        '  agreement "Semántica de custodia; clave transferId (P8)"\n'
        '  : TRAD -> NCG\n\n'
        '// Global connectors of the Rail Gateway (as in sos.arch)\n'),
    # C7: an internal service reaches the gateway without the translator.
    'c7-acl.arch': (
        'connector F_K25a nature dependency coupling blocking\n'
        '  carries "Consulta de estado consolidado de la carga (sale por SoS-K18a)"\n'
        '  : CRG -> TRAD -> LGW',
        '// Ill-formed (C7): carga-ms reaches the gateway without the canonical translator\n'
        'connector F_K25a nature dependency coupling blocking\n'
        '  carries "Consulta de estado consolidado de la carga (sale por SoS-K18a)"\n'
        '  : CRG -> LGW'),
    # C5: a queue whose load exceeds its capacity has no finite latency.
    'c5-queue-load.arch': (
        'component RSV "reservas-ms" in RLS tier T3 kind software capacity 12 load 8',
        '// Ill-formed (C5): the burst of F-QS7 exceeds the capacity of reservas-ms\n'
        'component RSV "reservas-ms" in RLS tier T3 kind software capacity 12 load 14'),
    # C5: the fixed stages use more exceedance than the percentile allows.
    'c5-percentile.arch': (
        'analysis FQS3CustodyLatency scenario "F-QS3" latency percentile 99 target 500 :',
        '// Ill-formed (C5): at p99.9 the two fixed stages already use 0.2 % of exceedance, '
        'more than the 0.1 % allowed\n'
        'analysis FQS3CustodyLatency scenario "F-QS3" latency percentile 99.9 target 500 :'),
    # C5 [F, as C]: a silence threshold without the cadence it counts.
    'c5-misses.arch': (
        '  carries "Ocupación de secciones de vía en el formato interno, solo cuando cambia (A11)"\n'
        '  : CON -> ILK',
        '  carries "Ocupación de secciones de vía en el formato interno, solo cuando cambia (A11)"\n'
        '  // Ill-formed (C5): three missed deliveries, but F-K11 has no cadence (A11)\n'
        '  misses 3\n'
        '  : CON -> ILK'),
    # C5 [F, as C]: a detection over a connector that declares no period nor misses.
    'c5-detection.arch': (
        '  F_K11 = unbounded, ILK',
        '  // Ill-formed (C5): F-K11 has no period and misses, so its silence has no detection time\n'
        '  F_K11, ILK'),
    # C5 [F]: a read through a blocking dependency that declares no read rate.
    'c5-read.arch': (
        '  RSV, TRN, POS, TRAD',
        '  // Ill-formed (C5): F-K22 does not declare the rate reservas-ms attains reading reservas-db\n'
        '  RSV reads RSVDB, TRN, POS, TRAD'),
    # C5 [F]: a read with a rate but no data flow that carries the reply.
    'c5-read-response.arch': [
        ('// Global connectors of the Rail Gateway (as in sos.arch)\n',
         'connector F_K22x nature dependency coupling blocking\n'
         '  carries "Lectura de la capacidad ya calculada"\n'
         '  capacity 40\n'
         '  : RSV -> RSVDB\n\n'
         '// Global connectors of the Rail Gateway (as in sos.arch)\n'),
        ('  RSV, TRN, POS, TRAD',
         '  // Ill-formed (C5): no data flow reservas-db -> reservas-ms carries the reply of F-K22x\n'
         '  RSV reads RSVDB, TRN, POS, TRAD'),
    ],
    # C5 [F]: two read paths with different rates for the same read.
    'c5-read-several.arch': [
        ('// Global connectors of the Rail Gateway (as in sos.arch)\n',
         'connector F_K22x nature dependency coupling blocking\n'
         '  carries "Lectura de la capacidad ya calculada"\n'
         '  capacity 40\n'
         '  : RSV -> RSVDB\n'
         'connector F_K22y nature dependency coupling blocking\n'
         '  carries "Lectura de la capacidad por otra réplica"\n'
         '  capacity 30\n'
         '  : RSV -> RSVDB\n'
         'connector F_K22z nature data_flow coupling blocking\n'
         '  carries "Capacidad calculada (respuesta)"\n'
         '  : RSVDB -> RSV\n\n'
         '// Global connectors of the Rail Gateway (as in sos.arch)\n'),
        ('  RSV, TRN, POS, TRAD',
         '  // Ill-formed (C5): F-K22x and F-K22y give two rates for the same read\n'
         '  RSV reads RSVDB, TRN, POS, TRAD'),
    ],
    # C5 [F, as C]: zero missed periods would detect a silence before it happens (syntax error).
    'c5-misses-zero.arch': (
        '  carries "Ocupación de secciones de vía en el formato interno, solo cuando cambia (A11)"\n'
        '  : CON -> ILK',
        '  carries "Ocupación de secciones de vía en el formato interno, solo cuando cambia (A11)"\n'
        '  // Ill-formed (C5): misses is a whole number of periods, at least 1\n'
        '  period 400 misses 0\n'
        '  : CON -> ILK'),

    # ---- Delivery 4 ----
    # C12: a branch of the fork goes on to a component it has no connector with.
    'c12-hop.arch': [parallel('F_K2p', 'RSV', 'CRG'), simulated(
        'X12', 'C12', 'reservas-ms answers the gateway directly, not through the translator',
        path='CTF -> [RSV | CRG] -> LGW')],
    # C13: the translator fails, but it has no capacity (it is a fixed stage).
    'c13-fault.arch': simulated(
        'X13', 'C13', 'a fault on the translator, which has no capacity',
        extra='  fault TRAD down at 60 for 60\n', measure='lost X13Jobs <= 0 events'),
    # C14: a quality scenario without its environment.
    'c14-parts.arch': (SCENARIO,
        '// Ill-formed (C14): the quality scenario has no environment\n'
        'scenario X14 "F-QS7"\n'
        '  source "Puertos y Carretera" stimulus "8 solicitudes de capacidad/s durante 30 min"\n'
        '  artifact LGW, TRAD, RSV, TRN, POS\n'
        '  response "Cada solicitud recibe capacidad o rechazo explícito"\n'
        '  verified_by FQS7CapacityRequest\n'),
    # C14: a simulated scenario without its run (auto_init: tested by replications).
    'c14-run.arch': (SCENARIO,
        '// Ill-formed (C14): a workload and a measure, but no run\n'
        'scenario X14R "F-QS7"\n'
        f'  workload X14RJobs rate 8 : {REQUEST}\n'
        '  measure p99_latency X14RJobs <= 800 ms\n'),
    # C15: a tactic motivated by a scenario declared not verifiable.
    'c15-tactic.arch': [
        (SCENARIO,
         'scenario X15 "F-QS6" attribute "evolucionabilidad"\n'
         '  source "Equipo dueño del modelo canónico" stimulus "Versión 2 del modelo canónico"\n'
         '  artifact TRAD environment "Operación normal"\n'
         '  response "Solo cambia el traductor"\n'
         '  not_verifiable "Versiones de interfaz por conector y comparación de dos modelos"\n'),
        (TACTIC,
         '// Ill-formed (C15): the tactic is motivated by a scenario whose measure is not verified\n'
         'tactic X15T "Capa anticorrupción" for X15 changes TRAD\n'),
    ],
    # C5 [F]: hit on a dependency without capacity.
    'c5-hit-capacity.arch': (
        '  carries "Lecturas y escrituras de los datos de cada servicio"\n'
        '  : TRN -> TRNDB',
        '  carries "Lecturas y escrituras de los datos de cada servicio"\n'
        '  // Ill-formed (C5): F-K22 declares no read rate, so no fraction is served at it\n'
        '  hit 0.9\n'
        '  : TRN -> TRNDB'),
    # C5 [F]: hit 0 (no read served by the dependency) is not a fraction in (0, 1].
    'c5-hit-range.arch': (GLOBAL,
        '// Ill-formed (C5): hit is a fraction in (0, 1]; 0 would declare a dependency never read\n'
        + READ.format(hit=' hit 0') + GLOBAL),
    # C5 [F]: vary hit on a dependency without capacity.
    'c5-vary-hit.arch': simulated(
        'X5V', 'C5', 'vary hit on F-K22, which declares no read rate',
        extra='  vary hit F_K22 : 1, 0.5\n'),
    # C5 [F]: in a workload, a read by a component that is not a queue.
    'c5-reads-queue.arch': [parallel('F_K2p', 'TRN', 'CRG'), simulated(
        'X5R', 'C5', 'trenes-ms reads trenes-db, but it is not a queue',
        path='CTF -> [TRN reads TRNDB | CRG] -> CTF')],
    # C5 [F]: a queue twice in the same path.
    'c5-queue-twice.arch': simulated(
        'X5Q', 'C5', 'the request goes through reservas-ms twice',
        path='LGW -> TRAD -> RSV -> TRAD -> RSV -> TRAD -> LGW'),
    # C5 [F]: drain on a workload with no store in its path.
    'c5-drain-store.arch': simulated(
        'X5D', 'C5', 'drain, but no store holds the requests while reservas-ms is down',
        extra='  fault RSV down at 60 for 60\n', measure='drain X5DJobs <= 300 s'),
    # C5 [F]: drain without a fault to drain after.
    'c5-drain-fault.arch': [
        ('component LGW "Rail Gateway" in RLS tier T2 kind software\n',
         'component LGW "Rail Gateway" in RLS tier T2 kind software store\n'),
        simulated('X5F', 'C5', 'drain, but nothing fails',
                  measure='drain X5FJobs <= 300 s'),
    ],
    # ---- Delivery 4, after the validation ----
    # C5 [F]: parallel on a data flow (the replies are not calls made at once).
    'c5-parallel-kind.arch': mark(
        'parallel on the replies of F-K23b, which is not a blocking dependency',
        'connector F_K23b nature data_flow coupling blocking\n'),
    # C5 [F]: parallel on a connector with a single link.
    'c5-parallel-links.arch': mark(
        'parallel on F-K3, which has a single link',
        'connector F_K3 nature dependency coupling blocking\n'),
    # C5 [F]: parallel on links that leave different sources.
    'c5-parallel-source.arch': mark(
        'parallel on F-K22, whose links leave four services',
        'connector F_K22 nature dependency coupling blocking\n'),
    # C5 [F]: a fork that no parallel connector enters (F-K23a is not parallel in rail-e1).
    'c5-fork-parallel.arch': simulated(
        'X5P', 'C5', 'a fork over the three services of C4, but F-K23a is not parallel in rail-e1',
        path=FORK),
    # C5 [F]: the three services of a parallel connector visited in sequence.
    'c5-parallel-sequence.arch': [parallel('F_K2p', 'RSV', 'CRG'), simulated(
        'X5S', 'C5', 'F-K2p is parallel, but the console visits its services one after another',
        path='CTF -> RSV -> CTF -> CRG -> CTF')],
    # C5 [F]: the store comes after the component that fails, so it holds nothing.
    'c5-drain-order.arch': [
        ('component LGW "Rail Gateway" in RLS tier T2 kind software\n',
         'component LGW "Rail Gateway" in RLS tier T2 kind software store\n'),
        simulated('X5O', 'C5', 'the store (the gateway) is after reservas-ms, which fails',
                  path='RSV -> TRAD -> LGW', extra='  fault RSV down at 60 for 60\n',
                  measure='drain X5OJobs <= 300 s'),
    ],
    # C14 [F]: a single replication gives no confidence interval.
    'c14-replications.arch': simulated(
        'X14N', 'C14', 'a single replication', run='600 warmup 60 replications 1'),
    # C14 [F]: the warm-up takes the whole run.
    'c14-warmup.arch': simulated(
        'X14W', 'C14', 'the warm-up is as long as the run', run='600 warmup 600 replications 2'),
}


def insert(text, kind, block):
    """Inserts a scenario before the first tactic (or at the end) and a tactic at the end."""
    if not text.endswith('\n'):
        text += '\n'
    first = re.search(r'^tactic\b', text, re.M) if kind == SCENARIO else None
    at = first.start() if first else len(text)
    return text[:at] + '\n' + block + text[at:]


if __name__ == '__main__':
    base = open(os.path.join(HERE, 'models', 'rail-e1.arch'), encoding='utf-8').read()
    for name, changes in CASES.items():
        # A case is one change (old, new) or a list of them.
        text = base
        for old, new in changes if isinstance(changes, list) else [changes]:
            if old in (SCENARIO, TACTIC):
                text = insert(text, old, new)
                continue
            assert base.count(old) == 1, f'{name}: the text to replace is not unique in rail-e1.arch'
            text = text.replace(old, new)
        with open(os.path.join(HERE, 'invalid', name), 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'invalid/{name} written')
