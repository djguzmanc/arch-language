"""P11. SoS-QS1 (M4) composed with the verified measures (Delivery 4, section 3.4).

Reads the analysis SoSQS1M4 of the joint model (models/sos.arch): reconciliation <= 900 s after
the recovery, as the chain RGW 200 s (Carretera) + SoS_K5 40 s + NCG 230 s (NCS) + SoS_K32 10 s
(notice) + CGW 300 s, where CGW stands for the four consumers that reconcile in parallel after
the notices SoS-K32..K35 (CPS, PPS, RLS, FTS; see the header of sos.arch). It writes
out/sos/sos-qs1.md with:

  1. Bottom-up: each stage of M4 (and each consumer) with its budget, the verified measure when
     one is known and its outcome against the budget. Known measures:
       - RLS (this team): the drain of F-QS1 (P3) verified by simulation on the final architecture
         (rail-e4, with T4.3); the measure before the redesign (rail-e3) is shown as evolution;
       - NCS (team D): recovery of ncs-e4, 183.8 s, 95 % CI [183.3; 184.3], as the joint agreement
         records it (section 1.3.3 of the common document). The repository of team D
         (out/ncs-e4/verification.md) publishes 184.9 [183.8; 186.1]; the report says so;
     every other stage counts its budget and is marked 'sin medida'.
  2. Top-down: 200 + 40 + NCS + 10 + max(consumers) against 900 s, with the budgets and with the
     verified measures (the ends of the CIs are added: a conservative composition of means).
  3. Sensitivity to the parameters of other owners: how far Carretera, the NCS, the boundary
     connectors and the consumers can grow before SoS-QS1 is violated or loses its margin.

Outcomes follow Laboratory 5: high <= 0.9 * threshold, satisfied with margin; high <= threshold,
satisfied without margin; low > threshold, violated; otherwise inconclusive.

Our drain and the recovery of team D are composed as they are, although their definitions differ:
recovery (Laboratory 5, team D) also counts the wait for the first arrival after the fault
(about 1/rate), drain does not. The report declares it.

Measure of the rail stage. By default it is read from out/rail-e4/verification.md (and the
evolution row from out/rail-e3/verification.md), written by
verification.py (agent SIMULADOR), which must contain one line with the marker

    RLS_RECONCILIATION_S <mean> <low> <high>

in seconds, decimal point, for the drain of F-QS1 with the nominal parameters of the model (the
first value of the vary, if any). The marker may sit inside an HTML comment or backticks; only
the first marker of the file is read. --rail MEAN LOW HIGH gives the measure by hand instead,
and --rail-from another report (--rail-before-from for the evolution row). Without a measure, the
rail stage counts its budget.

Usage:
    python sos_compose.py                                  # models/sos.arch, out/rail-e4 and e3
    python sos_compose.py --rail 143.0 135.0 151.0         # measure given by hand
    python sos_compose.py --ncs 184.9 183.8 186.1          # another measure of the NCS
"""
import argparse
import os
import re

from metamodel import create_metamodel, singles

ANALYSIS = 'SoSQS1M4'
RAIL = 'RLS'
# Notices "restablecido" from the NCS to the consumers (SoS-K32..K35): their targets reconcile
# in parallel; the first of them carries the stage in the analysis (CGW).
NOTICES = ('SoS_K32', 'SoS_K33', 'SoS_K34', 'SoS_K35')
NCS_E4 = (183.8, 183.3, 184.3)          # team D, ncs-e4, as in the joint agreement
NCS_SOURCE = 'acuerdo conjunto, sección 1.3.3 (documento común)'
NCS_NOTE = ('el repositorio del equipo D (`out/ncs-e4/verification.md`) publica para ncs-e4 '
            '184,9 s, IC [183,8; 186,1], y no 183,8 s [183,3; 184,3] como el acuerdo conjunto. '
            'La diferencia no cambia ninguna conclusión de este reporte (la holgura de SoS-QS1 '
            'es de más de 160 s) y debe resolverse en el acuerdo. `--ncs` cambia la cifra.')
RAIL_NOTE = ('T4.3 (reconciliación por camión) supone que SoS-K18a devuelve todas las unidades de '
             'un camión en una sola consulta; está por confirmar en el acuerdo conjunto. Si no se '
             'confirma, la cifra de rail-e3 (antes del rediseño) es la conservadora.')
DEFINITIONS = ('Definiciones distintas: el tramo del férreo es nuestro `drain` (desde el fin de la '
               'falla hasta que sale el último trabajo retenido) y el del NCS es el `recovery` del '
               'equipo D (Laboratorio 5), que además cuenta la espera de la primera llegada '
               'posterior a la falla (≈ 1/λ). Se componen tal como están: según el equipo D esa '
               'espera es de 0,67 s en su cuello de botella (CAR), así que la suma no cambia de '
               'forma apreciable, pero no son la misma medida.')
# What-if of other owners with measures already published (common/README.md, team D).
WHAT_IF = [
    ('NCS sin su rediseño (ncs-e2 de D)', 'NCS', (1932.8, 1921.5, 1944.1)),
]
MARKER = re.compile(r'RLS_RECONCILIATION_S\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)')


def fmt(x, digits=1):
    """Spanish number format: 1.932,8."""
    text = f'{x:,.{digits}f}'
    return text.replace(',', '_').replace('.', ',').replace('_', '.')


def outcome(low, high, threshold):
    if high <= 0.9 * threshold:
        return 'satisfecha con margen'
    if high <= threshold:
        return 'satisfecha sin margen'
    if low > threshold:
        return 'violada'
    return 'inconclusa'


def read_marker(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, encoding='utf-8') as f:
        found = MARKER.search(f.read())
    return tuple(float(x) for x in found.groups()) if found else None


def stages(joint):
    """The stages of M4: (name, constituent, budget in s)."""
    analysis = next(a for a in joint.analyses if a.name == ANALYSIS)
    found = []
    for factor in analysis.factors:
        for s in singles(factor):
            budget = s.value or s.ref.latency
            if s.unbounded or not budget:
                raise SystemExit(f'{ANALYSIS}: {s.ref.name} has no budget')
            if s.ref.__class__.__name__ == 'Component':
                owner = s.ref.system.name
            else:
                owner = 'acuerdo ' + '/'.join(sorted({c.system.name for l in s.ref.links
                                                      for c in l.path}))
            found.append((s.ref.name, owner, budget / 1000))
    return analysis.target / 1000, found


def consumers(joint, representative):
    """The gateways that reconcile in parallel: targets of the notices, with their constituent."""
    connectors = {e.name: e for e in joint.elements if e.__class__.__name__ == 'Connector'}
    found = [(connectors[n].links[0].path[-1].name, connectors[n].links[0].path[-1].system.name)
             for n in NOTICES if n in connectors]
    if representative not in [g for g, _ in found]:
        raise SystemExit(f'{representative} is not the target of a notice {NOTICES}')
    return found


def compose(chain, group, measures):
    """(mean, low, high) of the chain: series stages add, the consumers take their maximum."""
    def value(owner, budget):
        return measures.get(owner, (budget, budget, budget))
    serial = [value(owner, budget) for name, owner, budget in chain]
    parallel = [value(owner, budget) for _, owner, budget in group]
    return tuple(sum(v[i] for v in serial) + max(v[i] for v in parallel) for i in range(3))


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--joint', default='models/sos.arch')
    parser.add_argument('--rail', nargs=3, type=float, metavar=('MEAN', 'LOW', 'HIGH'))
    parser.add_argument('--rail-from', default='out/rail-e4/verification.md',
                        help='report with the marker of the final architecture (rail-e4)')
    parser.add_argument('--rail-before-from', default='out/rail-e3/verification.md',
                        help='report with the marker before the redesign (rail-e3), for the '
                             'evolution row; an empty value omits it')
    parser.add_argument('--ncs', nargs=3, type=float, metavar=('MEAN', 'LOW', 'HIGH'),
                        default=NCS_E4)
    parser.add_argument('--out', default='out/sos/sos-qs1.md')
    args = parser.parse_args()

    joint = create_metamodel().model_from_file(args.joint)
    target, found = stages(joint)
    *chain, (rep, rep_owner, consumer_budget) = found
    group = [(g, owner, consumer_budget) for g, owner in consumers(joint, rep)]

    rail = tuple(args.rail) if args.rail else read_marker(args.rail_from)
    rail_source = ('dado a mano (--rail)' if args.rail else
                   f'simulación, `{args.rail_from}` (P3, drain de F-QS1)' if rail else None)
    before = read_marker(args.rail_before_from)
    measures = {'NCS': tuple(args.ncs)}
    sources = {'NCS': NCS_SOURCE if tuple(args.ncs) == NCS_E4 else 'dado a mano (--ncs)'}
    if rail:
        measures[RAIL] = rail
        sources[RAIL] = rail_source

    lines = ['# SoS-QS1 (M4): composición con las medidas verificadas (P11)', '',
             f'Modelo: `{args.joint}`, análisis `{ANALYSIS}`. Medida de SoS-QS1 M4: reconciliación '
             f'≤ {fmt(target, 0)} s tras recuperar Carretera. Los consumidores ({", ".join(o for _, o, _ in group)}) '
             f'reconcilian en paralelo después de los avisos {", ".join(NOTICES)}, cada uno con '
             f'{fmt(consumer_budget, 0)} s; `{rep}` los representa en el análisis.', '',
             'Clasificación (Laboratorio 5): con margen si el extremo alto del IC ≤ 0,9 · umbral; '
             'sin margen si ≤ umbral; violada si el extremo bajo > umbral; si no, inconclusa.', '']

    # 1. Bottom-up
    lines += ['## 1. Bottom-up: medida verificada de cada tramo frente a su presupuesto', '',
              '| Tramo | Dueño | Presupuesto | Medida verificada | IC 95 % | Fuente | Resultado |',
              '|-------|-------|-------------|-------------------|---------|--------|-----------|']
    rows = [(name, owner, budget) for name, owner, budget in chain] + \
           [(f'{g} (consumidor)', owner, budget) for g, owner, budget in group]
    for name, owner, budget in rows:
        m = measures.get(owner)
        if m:
            lines.append(f'| {name} | {owner} | {fmt(budget, 0)} s | {fmt(m[0])} s | '
                         f'[{fmt(m[1])}; {fmt(m[2])}] | {sources[owner]} | '
                         f'{outcome(m[1], m[2], budget)} |')
        else:
            lines.append(f'| {name} | {owner} | {fmt(budget, 0)} s | sin medida | — | '
                         f'presupuesto | — |')
        if owner == RAIL and before:
            lines.append(f'| {name}, evolución: antes del rediseño (T4.3) | {owner} | '
                         f'{fmt(budget, 0)} s | {fmt(before[0])} s | '
                         f'[{fmt(before[1])}; {fmt(before[2])}] | simulación, '
                         f'`{args.rail_before_from}` (no entra en la composición) | '
                         f'{outcome(before[1], before[2], budget)} |')
    lines += ['', f'Nota sobre el NCS: {NCS_NOTE}', '', f'Nota sobre el férreo: {RAIL_NOTE}',
              '', DEFINITIONS]
    if not rail:
        lines += ['', f'No hay medida del férreo: falta el marcador `RLS_RECONCILIATION_S` en '
                      f'`{args.rail_from}`; el tramo {RAIL} cuenta su presupuesto.']

    # 2. Top-down
    budgets = compose(chain, group, {})
    verified = compose(chain, group, measures)
    formula = ' + '.join([fmt(b, 0) for _, _, b in chain]) + ' + máx(consumidores)'
    lines += ['', '## 2. Top-down: composición frente a la medida de SoS-QS1', '',
              f'Composición: {formula}. Con las medidas verificadas se suman los extremos de cada '
              f'IC (cota conservadora de la media compuesta, no un IC de la suma); el máximo de los '
              f'consumidores se toma extremo a extremo y un consumidor sin medida cuenta su '
              f'presupuesto.', '',
              '| Composición | NCS (alto) | máx(consumidores) (alto) | Total (media) | Total [bajo; alto] | Umbral | Resultado |',
              '|-------------|-----|--------------------|---------------|--------------------|--------|-----------|']

    def row(label, total, ncs, cons):
        return (f'| {label} | {fmt(ncs)} s | {fmt(cons)} s | {fmt(total[0])} s | '
                f'[{fmt(total[1])}; {fmt(total[2])}] | ≤ {fmt(target, 0)} s | '
                f'{outcome(total[1], total[2], target)} |')

    ncs_budget = next(b for _, o, b in chain if o == 'NCS')

    def cons_max(ms, i):
        return max(ms.get(o, (b, b, b))[i] for _, o, b in group)

    lines.append(row('Presupuestos (E2)', budgets, ncs_budget, consumer_budget))
    lines.append(row('Medidas verificadas', verified, measures['NCS'][2], cons_max(measures, 2)))
    if before:
        what = dict(measures, **{RAIL: before})
        lines.append(row('Medidas verificadas, férreo antes del rediseño (rail-e3)',
                         compose(chain, group, what), what['NCS'][2], cons_max(what, 2)))
    for label, owner, value in WHAT_IF:
        what = dict(measures, **{owner: value})
        lines.append(row(label, compose(chain, group, what), what['NCS'][2], cons_max(what, 2)))

    # 3. Sensitivity
    slack, margin = target - verified[2], 0.9 * target - verified[2]
    lines += ['', '## 3. Sensibilidad a parámetros de otros dueños', '',
              f'Sobre la composición con medidas verificadas (extremo alto {fmt(verified[2])} s): '
              f'holgura hasta violar {fmt(slack)} s; hasta perder el margen (0,9 · {fmt(target, 0)} = '
              f'{fmt(0.9 * target, 0)} s) {fmt(margin)} s. Cada fila varía un parámetro y deja los '
              f'demás como están.', '',
              '| Parámetro | Dueño | Valor actual | Con margen hasta | Violada por encima de | Crecimiento admisible |',
              '|-----------|-------|--------------|------------------|-----------------------|-----------------------|']
    for name, owner, budget in chain:
        if owner == RAIL:
            continue
        now = measures.get(owner, (budget, budget, budget))[2]
        kind = 'medida' if owner in measures else 'presupuesto'
        lines.append(f'| {name} | {owner} | {fmt(now)} s ({kind}) | {fmt(now + margin)} s | '
                     f'{fmt(now + slack)} s | +{fmt(slack)} s (+{fmt(100 * slack / now, 0)} %) |')
    now = cons_max(measures, 2)
    lines.append(f'| máx(consumidores) | {", ".join(o for _, o, _ in group)} | {fmt(now)} s | '
                 f'{fmt(now + margin)} s | {fmt(now + slack)} s | +{fmt(slack)} s '
                 f'(+{fmt(100 * slack / now, 0)} %) |')
    if rail:
        others = max(b for _, o, b in group if o != RAIL)
        lines += ['', f'Férreo: su extremo alto ({fmt(rail[2])} s) queda {fmt(others - rail[2])} s por '
                      f'debajo del presupuesto de los demás consumidores ({fmt(others, 0)} s), así '
                      f'que no fija el máximo del grupo; mientras los demás estén en su presupuesto, '
                      f'SoS-QS1 conserva el margen con el férreo hasta {fmt(now + margin)} s y se '
                      f'viola por encima de {fmt(now + slack)} s.']

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'{args.out} written (rail measure: {"none" if not rail else rail})')


if __name__ == '__main__':
    main()
