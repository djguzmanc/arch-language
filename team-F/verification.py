"""Verification of a model (Laboratory 5, section 4.4), team F (Rail), Delivery 4.

Based on verification.py of team D (common language). Runs the five steps of the verification
process: reads the model and checks its constraints (1. abstraction and 2. instantiation), draws
its graph by tier and checks the structural properties on it (3. graphing), runs the scenarios
and the Monte Carlo of availability (4. simulation), and writes the report (5. reporting), in
Spanish, to out/<model>/verification.md, with the graph in out/<model>/graph.png.

Structural properties [F]:
  S1  no single point of failure in the authorization chain C1 of F-QS5 (the components of its
      availability analyses, the on-board unit included, closed over the links that join them);
      the ground chain (without the on-board equipment, tier T5) is reported for information.
  S2  no blocking connector in the authorization cycle (artifact of F-QS4), as Laboratory 5.
  S3  every supply connector into a T3 of the authorization chain declares a period, so its
      silence can be detected (the rule of Delivery 3 for silent supply, as a property).
  S4  SoS-K34 reaches arribos-ms, and the component that fails in F-QS1 has a store right before
      it in the path of its workload (or is a store): the structure holds the units. Not evaluable
      when the model lacks SoS-K34, arribos-ms with capacity, or F-QS1 with its fault.

The report starts with a summary by property (S1–S4, P1–P11 that apply to the model, and the
scenarios declared not verifiable), lists warnings (a queue with ρ ≥ 1, a p99 that counts only
the jobs not lost), shows q_ef for F-QS1 and ends with a regression test of the simulator. With
two or more models it also writes out/evolution.md (each property across the iterations).

The report ends with a parseable line `RLS_RECONCILIATION_S <mean> <low> <high>` (seconds) when
the model has the drain measure of F-QS1; sos_compose.py reads it.

Usage: python3 verification.py [--out DIR] [models/<m>.arch ...]   (default: models/rail-e*.arch)
"""
import argparse
import glob
import hashlib
import math
import os
import re
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

from textx import get_location

from metamodel import FIXED_EXCEEDANCE, create_metamodel, singles
from simulation import (AVAILABILITY_SEED, MTTR_HOURS, WITH_MARGIN, WITHOUT_MARGIN, VIOLATED,
                        INCONCLUSIVE, analytic_availability, availability_factors,
                        availability_margin, build_plan, capacity_of, hops_of, interval,
                        known_result, model_value, outcome, outcome_availability,
                        regression_fifo, run_point, simulate_availability, utilization)
from transformations import _base_latency, _detection_stage, _stage

TIER_COLOR = {'T1': 'lightblue', 'T2': 'khaki', 'T3': 'lightgreen', 'T4': 'orange', 'T5': 'salmon'}
# [F] 1000 replications × 20 years: the half-width of the CI of P7 in rail-e4 (≈ 0.001 pp) is a
# quarter of its distance to the limit with margin, so the verdict does not change with the seed;
# it takes well under a second per analysis.
MC_YEARS, MC_REPLICATIONS = 20, 1000
ON_BOARD_TIER = 'T5'


def _kind(x):
    return x.__class__.__name__


def _components(model):
    return [e for e in model.elements if _kind(e) == 'Component']


def _connectors(model):
    return [e for e in model.elements if _kind(e) == 'Connector']


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _num(x, digits=1):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return '—'
    return f'{x:.{digits}f}'


def _value(v):
    return '—' if v is None else f'{v:g}'


def _measure_name(m):
    return f'{m.metric} {m.workload.name}' if m.workload else m.metric


def _starts(label, prefix):
    return label == prefix or label.startswith(prefix + ' ')


# ─────────────────────────────────────────────
# Step 3. Graphing (team D, unchanged)
# ─────────────────────────────────────────────

def build_graph(model):
    graph = nx.DiGraph()
    order = {s.name: i for i, s in enumerate(model.constituents)}
    for c in sorted(_components(model), key=lambda c: order[c.system.name]):
        graph.add_node(c.name, tier=c.tier, layer=-int(c.tier[1]))
    for k in _connectors(model):
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                graph.add_edge(a.name, b.name, label=k.name)
    return graph


def draw_graph(model, out):
    graph = build_graph(model)
    plt.figure(figsize=(16, 11))
    # [F] layers as ordered lists: with subset_key='layer' networkx groups the nodes in sets,
    # whose order depends on the hash seed, and the figure would change between runs
    layers = {}
    for n in graph.nodes:
        layers.setdefault(graph.nodes[n]['layer'], []).append(n)
    pos = nx.multipartite_layout(graph, subset_key=layers, align='horizontal')
    nx.draw(graph, pos, with_labels=True, node_size=1600, font_size=7, arrows=True,
            connectionstyle='arc3,rad=0.2', edge_color='gray',
            node_color=[TIER_COLOR[graph.nodes[n]['tier']] for n in graph.nodes])
    plt.title(f'{model.name} ({os.path.basename(out)}) — grafo C&C por tier')
    plt.savefig(os.path.join(out, 'graph.png'), dpi=150, bbox_inches='tight',
                metadata={'Software': None})
    plt.close()
    return graph


# ─────────────────────────────────────────────
# Structural properties, checked on the graph of the model
# ─────────────────────────────────────────────

def _factor_components(analysis):
    """Components that an analysis names, and those that its connectors traverse."""
    nodes = []
    for f in analysis.factors:
        for s in singles(f):
            r = s.ref
            if _kind(r) == 'Component':
                nodes.append(r.name)
            else:
                nodes += [c.name for link in r.links for c in link.path]
    return nodes


def closure(model, names):
    """[D4] The components, plus every component that a link traverses between two of them."""
    out = set(names)
    for k in _connectors(model):
        for link in k.links:
            p = link.path
            if len(p) >= 3 and p[0].name in names and p[-1].name in names:
                out |= {c.name for c in p[1:-1]}
    return out


def _replicated(analyses):
    """[F] Components replicated by an alternative of a group (no instances in team F)."""
    names = set()
    for a in analyses:
        for f in a.factors:
            if _kind(f) == 'Group' and len(f.alternatives) > 1:
                names |= {s.ref.name for s in f.alternatives}
    return names


def availability_sources(model):
    """(label, availability analyses) of the scenarios of F-QS5: those that a scenario verifies
    by an availability analysis; without such a scenario, the analyses of F-QS5 themselves."""
    sources = []
    for s in model.scenarios:
        checks = [a for a in s.checks if a.metric == 'availability']
        if checks:
            sources.append((f'{s.label} ({s.name})', checks))
    if not sources:
        checks = [a for a in model.analyses if a.metric == 'availability'
                  and _starts(a.scenario, 'F-QS5')]
        if checks:
            sources.append(('F-QS5 (análisis, sin escenario)', checks))
    return sources


def _tier(model):
    return {c.name: c.tier for c in _components(model)}


def check_s1(model):
    rows, chains = [], []
    tiers = _tier(model)
    for label, analyses in availability_sources(model):
        chain = closure(model, {n for a in analyses for n in _factor_components(a)})
        single = sorted(chain - _replicated(analyses))
        chains.append(chain)
        names = ', '.join(a.name for a in analyses)
        rows.append(('S1', 'Sin punto único de falla en la cadena de autorización C1 (OBU incluida)',
                     f'{label}: {names}', ', '.join(single) or 'ninguno',
                     VIOLATED if single else 'Satisfecha'))
        ground = sorted(n for n in single if tiers[n] != ON_BOARD_TIER)
        rows.append(('S1 (informativo)', 'Desglose: cadena de tierra (sin el equipo a bordo, T5)',
                     f'{label}: {names}', ', '.join(ground) or 'ninguno', VIOLATED if ground else 'Satisfecha'))
    return rows, set().union(*chains) if chains else set()


def check_s2(model):
    rows = []
    # the scenario of the authorization cycle, not a measure of F-QS4 declared not verifiable
    scenarios = [s for s in model.scenarios if _starts(s.label, 'F-QS4') and not s.missing]
    sources = []
    for s in scenarios:
        names = {e.name for e in s.artifact if _kind(e) == 'Component'}
        for a in s.checks:
            names |= set(_factor_components(a))
        sources.append((f'{s.label} ({s.name})', names))
    if not sources:
        for a in model.analyses:
            if _starts(a.scenario, 'F-QS4'):
                sources.append((f'{a.scenario} (análisis {a.name})', set(_factor_components(a))))
    for label, names in sources:
        chain = closure(model, names)
        blocking = sorted({k.name for k in _connectors(model) if k.coupling == 'blocking'
                           for link in k.links if {c.name for c in link.path} <= chain})
        rows.append(('S2', 'Sin conector bloqueante en el ciclo de autorización', label,
                     ', '.join(blocking) or 'ninguno', VIOLATED if blocking else 'Satisfecha'))
    if not rows:
        rows.append(('S2', 'Sin conector bloqueante en el ciclo de autorización', '—',
                     'no hay escenario ni análisis de F-QS4', NOT_EVALUABLE))
    return rows


def check_s3(model, chain):
    tiers = _tier(model)
    t3 = {n for n in chain if tiers[n] == 'T3'}
    silent = []
    for k in _connectors(model):
        if k.coupling != 'supply' or k.period or any(_crosses(link) for link in k.links):
            continue
        targets = sorted({link.path[-1].name for link in k.links} & t3)
        if targets:
            silent.append(f'{k.name} → {", ".join(targets)}')
    found = '; '.join(silent) or 'ninguno'
    return [('S3', 'Todo suministro hacia un T3 de la cadena de autorización declara period',
             f'F-QS2/F-QS5: T3 {", ".join(sorted(t3)) or "—"}', found,
             VIOLATED if silent else 'Satisfecha')]


def _reconciler(model):
    return next((c for c in _components(model) if c.label == 'arribos-ms' or c.name == 'ARR'), None)


def _resilience_scenario(model):
    """[F] The simulated scenario of F-QS1 (label or name), with or without drain."""
    for s in model.scenarios:
        if s.workloads and (_starts(s.label, 'F-QS1') or s.name == 'QS_F1'):
            return s
    return None


def _drain_scenario(model):
    for s in model.scenarios:
        if any(m.metric == 'drain' for m in s.measures):
            if _starts(s.label, 'F-QS1') or s.name == 'QS_F1':
                return s
    return None


NOT_EVALUABLE = 'No evaluable'
NOT_VERIFIABLE = 'No verificable'


def check_s4(model, graph):
    """[F] S4 on the structure: SoS-K34 reaches arribos-ms, and the component that fails in F-QS1
    has a store right before it in the path of its workload (or is a store itself), so the units
    that arrive during the fault are held, not lost. Without the elements it needs (SoS-K34,
    arribos-ms with capacity, the scenario F-QS1 with its fault) it is not evaluable."""
    label = 'S4'
    text = ('SoS-K34 alcanza arribos-ms y un store retiene las unidades antes del componente que '
            'falla en F-QS1')
    where = 'F-QS1 / SoS-QS1'
    arr = _reconciler(model)
    k34 = next((k for k in _connectors(model) if k.name == 'SoS_K34'), None)
    missing = []
    if k34 is None:
        missing.append('SoS_K34')
    if arr is None:
        missing.append('arribos-ms')
    elif not arr.capacity:
        missing.append(f'capacity de {arr.name}')
    s = _resilience_scenario(model)
    if s is None or not s.faults:
        missing.append('escenario F-QS1 simulado con su falla')
    if missing:
        return [(label, text, where, 'faltan en el modelo: ' + ', '.join(missing), NOT_EVALUABLE)]
    found, problems = [], []
    ends = sorted({link.path[-1].name for link in k34.links})
    reach = [e for e in ends if nx.has_path(graph, e, arr.name)]
    if reach:
        path = nx.shortest_path(graph, reach[0], arr.name)
        found.append('camino ' + ' → '.join([k34.links[0].path[0].name] + path))
    else:
        problems.append(f'SoS_K34 no alcanza {arr.name}')
    failing = {f.target.name for f in s.faults}
    for w in s.workloads:
        plan = build_plan(model, w.steps)
        for i, step in enumerate(plan):
            for b in step:
                if b.name not in failing:
                    continue
                if b.store:
                    found.append(f'{b.name} (falla) es store en {w.name}')
                elif b.prev_store:
                    prev = ', '.join(h.ref.name for h in hops_of(w.steps[i - 1]) if h.ref.store)
                    found.append(f'store {prev} justo antes de {b.name} (falla) en {w.name}')
                else:
                    problems.append(f'ningún store justo antes de {b.name} (falla) en {w.name}')
    return [(label, text, where, '; '.join(found + problems), VIOLATED if problems else 'Satisfecha')]


def check_structure(model, graph):
    s1, chain = check_s1(model)
    return s1 + check_s2(model) + check_s3(model, chain) + check_s4(model, graph)


# ─────────────────────────────────────────────
# Analyses of Delivery 3 as numbers (transformations.py gives them as text)
# ─────────────────────────────────────────────

def analytic_value(a):
    """Value of an analysis of Delivery 3: availability %, latency or detection in ms."""
    if a.metric == 'availability':
        return analytic_availability(availability_factors(a))
    if a.metric == 'detection':
        return sum(max(_detection_stage(s)[0] for s in singles(f)) for f in a.factors)
    if _base_latency(a):
        return sum(f.ref.latency for f in a.factors)
    exceedance = None
    if a.percentile:
        stages = [s for f in a.factors for s in singles(f)]
        fixed = sum(1 for s in stages if not s.store and (s.value or s.unbounded or s.ref.latency))
        queues = len(stages) - fixed
        if queues:
            exceedance = ((100 - a.percentile) - fixed * FIXED_EXCEEDANCE) / queues
    return sum(max(_stage(s, exceedance)[0] for s in singles(f)) for f in a.factors)


def classify_analysis(a, value):
    """[F] A point value with the margin of 10 %: of the threshold, or of the unavailability."""
    if a.metric == 'availability':
        if value >= a.target + availability_margin(a.target):
            return WITH_MARGIN
        return WITHOUT_MARGIN if value >= a.target else VIOLATED
    if value <= 0.9 * a.target:
        return WITH_MARGIN
    return WITHOUT_MARGIN if value <= a.target else VIOLATED


def _analysis_unit(a):
    return '%' if a.metric == 'availability' else 'ms'


# ─────────────────────────────────────────────
# Step 4. Simulation and Monte Carlo
# ─────────────────────────────────────────────

def simulate_scenarios(model):
    """For every simulated scenario: [(value, {measure: samples})]."""
    out = []
    for s in model.scenarios:
        if not (s.workloads and s.measures and s.replications):
            continue
        values = list(s.vary.values) if s.vary else [None]
        out.append((s, [(v, run_point(s, v)) for v in values]))
    return out


def check_availability(model):
    analyses, seen = [], set()
    for s in model.scenarios:
        for a in s.checks:
            if a.metric == 'availability' and a.name not in seen:
                analyses.append((s, a))
                seen.add(a.name)
    for a in model.analyses:
        if a.metric == 'availability' and a.name not in seen:
            analyses.append((None, a))
            seen.add(a.name)
    rows = []
    for i, (s, a) in enumerate(analyses):
        seed = AVAILABILITY_SEED + i
        values, exact = simulate_availability(a, seed, MC_YEARS, MC_REPLICATIONS)
        mean, low, high = interval(values)
        rows.append((s, a, seed, len(values), mean, low, high, exact,
                     outcome_availability(low, high, a.target)))
    return rows



# ─────────────────────────────────────────────
# [F] Effective query rate of F-QS1, warnings, and the summary by property
# ─────────────────────────────────────────────

QEF = re.compile(r'1/\(1/q(?:_ef)?\s*\+\s*(?:([0-9.]+)\s*x\s*)?([0-9.]+)\s*s\)')


def qef_formula(component):
    """[F] The formula of the rate of the reconciler, read from the comment that documents it
    right above the component in the model: 1/(1/q + t s) or 1/(1/q + k x t s). Returns
    (overhead in s, text of the formula, line) or None. Comments are not part of the metamodel,
    so the report shows the formula and its line as a documented assumption of the model."""
    loc = get_location(component)
    with open(loc['filename'], encoding='utf-8') as f:
        lines = f.read().splitlines()
    i = loc['line'] - 2
    block = []
    while i >= 0 and lines[i].strip().startswith('//'):
        block.append((i + 1, lines[i].strip()[2:].strip()))
        i -= 1
    for number, text in reversed(block):
        m = QEF.search(text)
        if m:
            k = float(m.group(1)) if m.group(1) else 1.0
            t = float(m.group(2))
            return k * t, m.group(0), number
    return None


def qef(capacity, overhead):
    """q_ef from the rate of the server: capacity = 1/(1/q_ef + overhead)."""
    rest = 1.0 / capacity - overhead
    return 1.0 / rest if rest > 0 else math.inf


def scenario_warnings(s, points):
    """[F] Visible warnings of a simulated scenario."""
    out = []
    if s.warmup >= s.duration:
        out.append(f'calentamiento ({s.warmup:g} s) ≥ corrida ({s.duration:g} s): ninguna llegada '
                   'cuenta para p99 ni lost')
    if s.replications < 2:
        out.append('una sola réplica: sin IC (el intervalo es el punto)')
    for value, samples in points:
        for name, lam, mu, rho in utilization(s, value):
            if rho >= 1:
                out.append(f'valor {_value(value)}: la cola {name} tiene ρ = {lam:g}/{mu:.4g} = '
                           f'{rho:.3f} ≥ 1 (inestable): la latencia crece con la corrida y el IC '
                           'no estima un régimen estacionario')
        lost = [m for m in s.measures if m.metric == 'lost' and max(samples[m]) > 0]
        p99 = [m for m in s.measures if m.metric == 'p99_latency']
        if p99 and (lost or s.faults):
            n = max((max(samples[m]) for m in lost), default=None)
            detail = f'hasta {n:g} perdidos por réplica' if n is not None else 'hay falla en el escenario'
            out.append(f'valor {_value(value)}: el p99 cuenta solo los trabajos no perdidos ({detail})')
    return out


def _point(s, points):
    base = model_value(s)
    return next(((v, smp) for v, smp in points if v == base), points[0])


PROPERTIES = [
    # id, kind, key, name
    ('P1', 'sim', ('QS_F7', 'p99_latency'), 'p99 de la solicitud de capacidad (F-QS7)'),
    ('P2', 'sim', ('QS_F3', 'p99_latency'), 'p99 de la custodia durante la ráfaga (F-QS3)'),
    ('P3', 'sim', ('QS_F1', 'drain'), 'Reconciliación (drain) tras la caída de 4 h (F-QS1)'),
    ('P4', 'sim', ('QS_F1', 'lost'), 'Unidades perdidas en la caída (F-QS1)'),
    ('P5', 'an', 'FQS1StaleData', 'Detección de datos viejos (F-QS1)'),
    ('P6', 'mc', 'FQS5AuthorizationAvailability', 'Disponibilidad de la cadena C1 (F-QS5)'),
    ('P7', 'mc', 'FQS5WithTrack', 'Disponibilidad de C1 con la vía (F-QS5)'),
    ('P8', 'an', 'FQS5Takeover', 'Toma de control de SAM-B (F-QS5)'),
    ('P9', 'an', 'FQS2SilentConcentrator', 'Detección del concentrador callado (F-QS2)'),
    ('P9b', 'an', 'FQS2Routes', 'Detección del estado de rutas callado (F-QS2, it. 4)'),
    ('P10', 'an', 'FQS4AuthorizationCycle', 'Ciclo de autorización p99 (F-QS4)'),
    ('P11', 'an', 'SoSQS1M4', 'SoS-QS1 M4 compuesto (presupuestos; P3 bottom-up)'),
]


def summary(model, structure, availability, simulations):
    """[F] One row per property that applies to the model: (id, property, scenario, technique,
    estimate, CI, threshold, outcome)."""
    rows = []
    for i, p, where, found, result in structure:
        if i.startswith('S') and 'informativo' not in i:
            rows.append((i, p, where, 'G (grafo)', found, '—', '0 elementos' if i != 'S4' else 'camino y store', result))
    sims = {s.name: (s, points) for s, points in simulations}
    mc = {a.name: row for row in availability for a in [row[1]]}
    analyses = {a.name: a for a in model.analyses}
    for pid, kind, key, name in PROPERTIES:
        if kind == 'sim':
            if key[0] not in sims:
                continue
            s, points = sims[key[0]]
            ms = [m for m in s.measures if m.metric == key[1]]
            if not ms:
                continue
            m = ms[0]
            value, samples = _point(s, points)
            mean, low, high = interval(samples[m])
            tech = 'SIM (DES)' + (f', valor del modelo {_value(value)}; sensibilidad en §3' if s.vary else '')
            rows.append((pid, name, f'{s.label} ({s.name})', tech, f'{_num(mean)} {m.unit}',
                         f'[{_num(low)}; {_num(high)}]', f'≤ {m.threshold:g} {m.unit}',
                         outcome(low, high, m.threshold)))
        elif kind == 'mc':
            if key not in mc:
                continue
            s, a, seed, n, mean, low, high, exact, result = mc[key]
            rows.append((pid, name, s.label if s else a.scenario,
                         f'MC ({n} × {MC_YEARS} años, semilla {seed}); Lab 3 = {exact:.4f} % como conocido',
                         f'{mean:.4f} %', f'[{low:.4f}; {high:.4f}]', f'≥ {a.target:g} %', result))
        else:
            a = analyses.get(key)
            if a is None:
                continue
            v = analytic_value(a)
            unit = 's' if v >= 100000 else 'ms'
            shown = v / 1000 if unit == 's' else v
            target = a.target / 1000 if unit == 's' else a.target
            tech = 'AN (E3)'
            if pid == 'P11':
                drain = next((r for r in rows if r[0] == 'P3'), None)
                if drain:
                    bottom = f'bottom-up: P3 = {drain[4]}, IC {drain[5]} frente a 300 s ({drain[7]})'
                else:
                    bottom = 'bottom-up: P3 sin simular'
                tech = f'AN (presupuestos E3); {bottom}; composición en out/sos/sos-qs1.md'
            rows.append((pid, name, a.scenario, tech, 'ilimitado' if math.isinf(v) else f'{shown:.1f} {unit}',
                         '— (valor puntual)', f'≤ {target:g} {unit}',
                         VIOLATED if math.isinf(v) else classify_analysis(a, v)))
    for s in model.scenarios:
        if s.missing:
            rows.append((s.name, s.label, s.attribute or '—', '—', '—', '—', '—',
                         f'{NOT_VERIFIABLE}: {s.missing}'))
    return rows


def write_evolution(results, path):
    """[F] Table of each property across the models verified in one run (the iterations)."""
    names = [n for n, _ in results]
    order, label = [], {}
    for _, rows in results:
        for r in rows:
            if r[0] not in label:
                order.append(r[0])
                label[r[0]] = r[1]
    canonical = ['S1', 'S2', 'S3', 'S4'] + [p[0] for p in PROPERTIES]
    order.sort(key=lambda pid: (canonical.index(pid) if pid in canonical else len(canonical),))
    lines = ['# Evolución de las propiedades por iteración', '',
             'Generado por verification.py al verificar varios modelos en una corrida. Cada celda: '
             'resultado (estimación). «—»: la propiedad no aplica a ese modelo.', '',
             '| Id | Propiedad | ' + ' | '.join(names) + ' |',
             '|---|---|' + '---|' * len(names)]
    for pid in order:
        cells = []
        for _, rows in results:
            r = next((x for x in rows if x[0] == pid), None)
            if r is None:
                cells.append('—')
            elif r[7].startswith(NOT_VERIFIABLE):
                cells.append(NOT_VERIFIABLE)
            elif r[3].startswith('G'):
                cells.append(r[7])
            else:
                cells.append(f'{r[7]} ({r[4]})')
        lines.append(f'| {pid} | {label[pid]} | ' + ' | '.join(cells) + ' |')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Step 5. Reporting
# ─────────────────────────────────────────────

def _version(source):
    """The comment that names the iteration (or the first comment), joined until its sentence
    ends, and a short SHA-256 of the file."""
    with open(source, encoding='utf-8') as f:
        text = f.read()
    digest = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
    comments = []
    for line in text.splitlines():
        line = line.strip()
        comments.append(line[2:].strip() if line.startswith('//') else None)
    tagged = [i for i, c in enumerate(comments) if c and ('iteraci' in c.lower() or 'versi' in c.lower())]
    first = [i for i, c in enumerate(comments) if c]
    if not (tagged or first):
        return '—', digest
    i = (tagged or first)[0]
    parts = []
    while i < len(comments) and comments[i] and len(parts) < 4:
        parts.append(comments[i])
        if comments[i].endswith('.'):
            break
        i += 1
    return ' '.join(parts), digest


def _seeds(n):
    return f'{n} (semillas 1–{n})'


def report(model, source, structure, availability, simulations, out, rows):
    version, digest = _version(source)
    comps, conns = _components(model), _connectors(model)
    lines = [f'# Verificación de {model.name} — `{os.path.basename(source)}`', '',
             '## Resumen por propiedad', '',
             'Resultado en las categorías del Lab 5 (con margen, sin margen, inconclusa, violada) y '
             'no verificable. Las propiedades estructurales y las de umbral 0 (lost) no tienen margen: '
             '«Satisfecha». «No evaluable»: al modelo le faltan los elementos que la propiedad usa. '
             'P5, P8–P11 son valores puntuales del análisis de la Entrega 3 (sin IC).', '',
             '| Id | Propiedad | Escenario | Técnica | Estimación | IC 95 % | Umbral | Resultado |',
             '|---|---|---|---|---|---|---|---|']
    lines += ['| ' + ' | '.join(r) + ' |' for r in rows]
    lines += ['',
             '## 1. Alcance', '',
             f'- Modelo: `{source}` (sistema `{model.name}`, constituyente RLS).',
             f'- Versión del modelo: {version}',
             f'- Huella SHA-256 del archivo: `{digest}`.',
             f'- Contenido: {len(comps)} componentes, {len(conns)} conectores, '
             f'{len(model.analyses)} análisis, {len(model.scenarios)} escenarios, '
             f'{len(model.tactics)} tácticas.',
             '- Grafo C&C por tier: `graph.png`.',
             '- Simulación: eventos discretos (colas FIFO con servicio exponencial, llegadas Poisson); '
             'réplicas independientes con semillas 1..n; IC 95 % con t de Student; resultado con '
             'margen del 10 % del umbral.',
             f'- Disponibilidad: Monte Carlo de fallas y reparaciones, {MC_REPLICATIONS} réplicas × '
             f'{MC_YEARS} años, MTTR {MTTR_HOURS:g} h (supuesto), semillas {AVAILABILITY_SEED} + i; '
             'margen = 10 % de la indisponibilidad permitida.',
             '',
             '## 2. Propiedades estructurales (grafo)', '',
             '| Id | Propiedad | Escenario | Elementos encontrados | Resultado |',
             '|----|-----------|-----------|-----------------------|-----------|']
    lines += [f'| {i} | {p} | {s} | {e} | {o} |' for i, p, s, e, o in structure]

    # 3. Simulated scenarios
    lines += ['', '## 3. Escenarios simulados', '']
    if not simulations:
        lines += ['El modelo no tiene escenarios simulados.']
    for s, points in simulations:
        v = s.vary
        varied = '—'
        if v is not None:
            kind = 'hit de ' if v.hit else ('tasa de ' if _kind(v.target) == 'Workload'
                                            else 'capacity de ')
            varied = f'{kind}{v.target.name} (modelo: {_value(model_value(s))})'
        lines += [f'### {s.label} ({s.name})', '',
                  f'Corrida {s.duration:g} s, calentamiento {s.warmup:g} s, '
                  f'{_seeds(s.replications)}; parámetro variado: {varied}.', '']
        for w in s.workloads:
            lines.append(f'- Workload `{w.name}` (tasa {w.rate:g}/s): '
                         + ' → '.join('[' + ' | '.join(_hop(h) for h in hops_of(st)) + ']'
                                      if _kind(st) == 'Fork' else _hop(st) for st in w.steps))
        for f in s.faults:
            lines.append(f'- Falla: {f.target.name} caído desde {f.start:g} s durante {f.length:g} s')
        formula = None
        if v is not None and _kind(v.target) == 'Component' and any(m.metric == 'drain' for m in s.measures):
            formula = qef_formula(v.target)
            if formula:
                overhead, text, number = formula
                lines.append(f'- q_ef (consultas/s efectivas) derivada de la capacity de {v.target.name} con la '
                             f'fórmula documentada en el modelo (comentario de la línea {number}): '
                             f'capacity = {text}, es decir q_ef = 1/(1/capacity − {overhead:g} s). '
                             'Supuesto declarado del modelo (los comentarios no son parte del metamodelo).')
            else:
                lines.append(f'- q_ef: el modelo no documenta la fórmula de la capacity de {v.target.name}; '
                             'no se deriva.')
        qcol = formula is not None
        lines += ['', '| Valor | ' + ('q_ef (consultas/s) | ' if qcol else '') +
                  'Medida | Estimación | IC 95 % | Umbral | Resultado | Réplicas (semillas) |',
                  '|---|' + ('---|' if qcol else '') + '---|---|---|---|---|---|']
        for value, samples in points:
            for m in s.measures:
                mean, low, high = interval(samples[m])
                q = f'{qef(value, formula[0]):.2f} | ' if qcol else ''
                lines.append(f'| {_value(value)} | {q}{_measure_name(m)} | {_num(mean)} {m.unit} | '
                             f'[{_num(low)}; {_num(high)}] | ≤ {m.threshold:g} {m.unit} | '
                             f'{outcome(low, high, m.threshold)} | {_seeds(len(samples[m]))} |')
        warnings = scenario_warnings(s, points)
        if warnings:
            lines += [''] + [f'> **Aviso:** {w}' for w in warnings]
        lines.append('')

    # 4. Availability
    lines += ['## 4. Disponibilidad (Monte Carlo de fallas y reparaciones)', '']
    if availability:
        lines += ['| Escenario | Análisis | Semilla | Réplicas | Estimación | IC 95 % | '
                  'Conocido (fórmula Lab 3) | Umbral | Con margen desde | Resultado |',
                  '|---|---|---|---|---|---|---|---|---|---|']
        for s, a, seed, n, mean, low, high, exact, result in availability:
            lines.append(f'| {s.label if s else a.scenario} | {a.name} | {seed} | {n} × {MC_YEARS} años | '
                         f'{mean:.4f} % | [{low:.4f}; {high:.4f}] | {exact:.4f} % | ≥ {a.target:g} % | '
                         f'{100 - 0.9 * (100 - a.target):.4f} % | {result} |')
    else:
        lines.append('El modelo no tiene análisis de disponibilidad.')

    # 5. Known results
    lines += ['', '## 5. Chequeo contra resultado conocido (Lab 5, §4.6)', '',
              '| Caso | Fórmula | Conocido | Estimación | IC 95 % | ¿Dentro del IC? |',
              '|------|---------|----------|------------|---------|-----------------|']
    known_rows = 0
    for s, points in simulations:
        for value, samples in points:
            for m in s.measures:
                k, _ = known_result(s, m, value)
                if k is None:
                    continue
                mean, low, high = interval(samples[m])
                case = f'{s.name} {_measure_name(m)}' + ('' if value is None else f' ({_value(value)})')
                refs = [(k['formula'], k['value'])]
                if 'second' in k:
                    refs.append((k['second_formula'], k['second']))
                for formula, kv in refs:
                    inside = 'sí' if low - 1e-9 <= kv <= high + 1e-9 else 'no'
                    lines.append(f'| {case} | {formula} | {_num(kv)} {m.unit} | {_num(mean)} | '
                                 f'[{_num(low)}; {_num(high)}] | {inside} |')
                    known_rows += 1
    for s, a, seed, n, mean, low, high, exact, result in availability:
        inside = 'sí' if low <= exact <= high else 'no'
        lines.append(f'| {a.name} (MC, semilla {seed}) | Lab 3: Π(1 − u), grupo β·u + ((1 − β)·u)^n | '
                     f'{exact:.4f} % | {mean:.4f} | [{low:.4f}; {high:.4f}] | {inside} |')
        known_rows += 1
    if not known_rows:
        lines.append('| — | — | — | — | — | — |')
    outside = sum(1 for line in lines if line.endswith('| no |'))
    if outside:
        lines += ['', f'{outside} chequeo(s) fuera del IC. Con IC del 95 %, alrededor de 1 de cada 20 '
                  'chequeos correctos cae fuera por azar; se reporta tal cual, sin cambiar semillas.']
    lines += ['', 'Los casos sin fórmula cerrada (p. ej. 0 < hit < 1: servicio hiperexponencial) '
              'no se listan.']

    # 6. Analytic of Delivery 3 vs simulated
    lines += ['', '## 6. Analítico de la Entrega 3 frente a simulado', '',
              '| Escenario | Análisis E3 | Analítico E3 | Valor simulado | Estimación | IC 95 % | Observación |',
              '|---|---|---|---|---|---|---|']
    rows = 0
    for s, points in simulations:
        latency = [a for a in s.checks if a.metric == 'latency' and a.percentile]
        p99 = [m for m in s.measures if m.metric == 'p99_latency']
        if not latency or not p99:
            continue
        base = model_value(s)
        point = next(((v, smp) for v, smp in points if v == base), points[0])
        for a in latency:
            av = analytic_value(a)
            for m in p99:
                mean, low, high = interval(point[1][m])
                factor = 1000.0 if m.unit == 's' else 1.0
                av_unit = av / factor
                note = ('el analítico (Boole, cota) ≥ IC alto' if av_unit >= high
                        else 'el analítico cae en el IC' if low <= av_unit <= high
                        else 'el analítico < IC bajo: el análisis subestima')
                lines.append(f'| {s.label} | {a.name} (p{a.percentile:g}) | {_num(av_unit)} {m.unit} | '
                             f'{_value(point[0])} | {_num(mean)} {m.unit} | [{_num(low)}; {_num(high)}] | '
                             f'{note} |')
                rows += 1
    if not rows:
        lines.append('| — | — | — | — | — | — | — |')

    # 7. load vs workload rate
    lines += ['', '## 7. Consistencia de `load` (análisis E3) con las tasas de los workloads', '',
              'Aviso, no rechazo: la simulación toma las llegadas solo de los workloads; `load` lo usa '
              'el análisis de la Entrega 3.', '',
              '| Escenario | Cola | capacity | load (E3) | Σ tasas de los workloads | Estado |',
              '|---|---|---|---|---|---|']
    rows = 0
    for s in model.scenarios:
        totals = {}
        for w in s.workloads:
            for step in w.steps:
                for h in hops_of(step):
                    if capacity_of(h.ref):
                        totals[h.ref.name] = totals.get(h.ref.name, 0.0) + w.rate
        comps = {c.name: c for c in _components(model)}
        for name, total in totals.items():
            c = comps[name]
            if not c.load:
                state = 'sin load declarado'
            elif abs(total - c.load) <= 0.01 * max(c.load, total):
                state = 'coincide'
            else:
                state = f'AVISO: difiere ({total / c.load:.2f} × load)'
            lines.append(f'| {s.name} | {name} | {c.capacity:g} | {_value(c.load or None)} | {total:g} | {state} |')
            rows += 1
    if not rows:
        lines.append('| — | — | — | — | — | — |')

    # 8. Analyses of Delivery 3 named in verified_by
    lines += ['', '## 8. Análisis de la Entrega 3 nombrados en `verified_by`', '',
              'Valor puntual del análisis, clasificado con margen del 10 % (del umbral, o de la '
              'indisponibilidad permitida). **Informativo**: cuando la propiedad se simula o se '
              'estima por Monte Carlo (disponibilidad: §4), el veredicto es el de la simulación o el '
              'MC; aquí el analítico es solo referencia (resultado conocido o cota).', '',
              '| Escenario | Análisis | Métrica | Valor | Umbral | Resultado |',
              '|---|---|---|---|---|---|']
    rows = 0
    for s in model.scenarios:
        for a in s.checks:
            v = analytic_value(a)
            unit = _analysis_unit(a)
            shown = f'{v:.4f} %' if unit == '%' else ('ilimitado' if math.isinf(v) else f'{v:.1f} ms')
            cmp = '≥' if a.metric == 'availability' else '≤'
            result = VIOLATED if math.isinf(v) else classify_analysis(a, v)
            lines.append(f'| {s.label} ({s.name}) | {a.name} | {a.metric} | {shown} | {cmp} {a.target:g} {unit} | {result} |')
            rows += 1
    if not rows:
        lines.append('| — | — | — | — | — | — |')

    # 9. Not verifiable
    declared = [s for s in model.scenarios if s.missing]
    lines += ['', '## 9. Escenarios no verificables con este lenguaje', '']
    if declared:
        lines += ['| Escenario | Atributo | Qué falta |', '|---|---|---|']
        lines += [f'| {s.label} ({s.name}) | {s.attribute or "—"} | {s.missing} |' for s in declared]
    else:
        lines.append('Ninguno declarado.')

    # 10. Tactics
    lines += ['', '## 10. Tácticas declaradas', '']
    if model.tactics:
        lines += ['| Táctica | Para | Introduce | Cambia |', '|---|---|---|---|']
        for t in model.tactics:
            lines.append(f'| {t.label} ({t.name}) | {", ".join(s.label for s in t.scenarios)} | '
                         f'{", ".join(e.name for e in t.introduces) or "—"} | '
                         f'{", ".join(e.name for e in t.changes) or "—"} |')
    else:
        lines.append('Ninguna declarada.')

    lines += ['', '## 11. Prueba de regresión del simulador (orden FIFO con forks)', '',
              'Workload A: [Q1 | Q2 alcanzada 0,5 s después]; workload B directo a Q2 (5/s; Q2 atiende '
              '10/s y recibe 6/s). Cada cola debe atender sus llegadas en orden de tiempo: la estancia '
              'media de B en Q2 es la de una M/M/1, 1/(10 − 6) = 0,25 s, con o sin el retardo de A.', '',
              '| Retardo de A hacia Q2 | Estancia media de B | IC 95 % | Conocido | ¿Dentro? |',
              '|---|---|---|---|---|']
    for pre, mean, low, high, known, inside in regression_fifo():
        lines.append(f'| {pre:g} s | {mean:.4f} s | [{low:.4f}; {high:.4f}] | {known:g} s | '
                     f'{"sí" if inside else "NO"} |')

    rls = reconciliation(model, simulations)
    if rls is not None:
        lines += ['', f'RLS_RECONCILIATION_S {rls[0]:.2f} {rls[1]:.2f} {rls[2]:.2f}']
    with open(os.path.join(out, 'verification.md'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def _hop(h):
    return h.ref.name + (f' reads {h.store.name}' if h.store else '')


def reconciliation(model, simulations):
    """(mean, low, high) in seconds of the drain of F-QS1 at the value of the model."""
    s = _drain_scenario(model)
    if s is None:
        return None
    points = next(p for sc, p in simulations if sc is s)
    base = model_value(s)
    value, samples = next(((v, smp) for v, smp in points if v == base), points[0])
    m = next(m for m in s.measures if m.metric == 'drain')
    factor = 1000.0 if m.unit == 'ms' else 1.0
    mean, low, high = interval(samples[m])
    return mean / factor, low / factor, high / factor


def verify(model, source, root='out'):
    out = os.path.join(root, os.path.splitext(os.path.basename(source))[0])
    os.makedirs(out, exist_ok=True)
    graph = draw_graph(model, out)                                          # Step 3
    structure = check_structure(model, graph)
    availability = check_availability(model)                                # Step 4
    simulations = simulate_scenarios(model)
    rows = summary(model, structure, availability, simulations)
    report(model, source, structure, availability, simulations, out, rows)  # Step 5
    return out, rows


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Verificación de modelos del equipo F (Lab 5): grafo, propiedades S1–S4, '
                    'simulación, Monte Carlo de disponibilidad y reporte out/<modelo>/verification.md. '
                    'Con dos o más modelos escribe además out/evolution.md.')
    parser.add_argument('models', nargs='*', help='modelos .arch (por defecto: models/rail-e*.arch)')
    parser.add_argument('--out', default='out', help='carpeta de salida (por defecto: out)')
    args = parser.parse_args(argv)
    sources = args.models or sorted(glob.glob('models/rail-e*.arch'))
    mm = create_metamodel()
    results = []
    for source in sources:
        model = mm.model_from_file(source)                                  # Steps 1 and 2
        out, rows = verify(model, source, args.out)
        results.append((os.path.splitext(os.path.basename(source))[0], rows))
        print(f'{source}: reporte de verificación en {out}/verification.md')
    if len(results) > 1:
        path = os.path.join(args.out, 'evolution.md')
        write_evolution(results, path)
        print(f'evolución de las propiedades en {path}')


if __name__ == '__main__':
    main()
