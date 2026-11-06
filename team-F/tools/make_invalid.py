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
}

if __name__ == '__main__':
    base = open(os.path.join(HERE, 'models', 'rail-e1.arch'), encoding='utf-8').read()
    for name, (old, new) in CASES.items():
        assert base.count(old) == 1, f'{name}: the text to replace is not unique in rail-e1.arch'
        with open(os.path.join(HERE, 'invalid', name), 'w', encoding='utf-8') as f:
            f.write(base.replace(old, new))
        print(f'invalid/{name} written')
