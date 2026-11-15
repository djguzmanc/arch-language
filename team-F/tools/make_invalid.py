"""Writes the ill-formed models of invalid/ from models/rail-e1.arch, one change each.

Run it from team-F/ whenever rail-e1.arch changes, then regenerate the expected messages:
    python tools/make_invalid.py
    for f in invalid/*.arch; do python generation.py $f; done > invalid/expected-rejections.txt
"""
import os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
}

if __name__ == '__main__':
    base = open(os.path.join(HERE, 'models', 'rail-e1.arch'), encoding='utf-8').read()
    for name, changes in CASES.items():
        # A case is one change (old, new) or a list of them.
        text = base
        for old, new in changes if isinstance(changes, list) else [changes]:
            assert base.count(old) == 1, f'{name}: the text to replace is not unique in rail-e1.arch'
            text = text.replace(old, new)
        with open(os.path.join(HERE, 'invalid', name), 'w', encoding='utf-8') as f:
            f.write(text)
        print(f'invalid/{name} written')
