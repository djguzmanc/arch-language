import math
import os

from metamodel import FIXED_EXCEEDANCE, singles

NATURE = {
    'data_flow': 'data flow',
    'control_command': 'control command',
    'dependency': 'dependency',
    'event_notification': 'event notification',
}


def _components(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Component']


def _connectors(model):
    return [e for e in model.elements if e.__class__.__name__ == 'Connector']


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _boundary(connector):
    crossing = [link for link in connector.links if _crosses(link)]
    if not crossing:
        return 'No'
    if len(crossing) == len(connector.links):
        return 'Yes'
    return 'Yes (' + ', '.join(link.path[0].label for link in crossing) + ')'


# ─────────────────────────────────────────────
# Model-to-text: documentation (Laboratory 4, unchanged)
# ─────────────────────────────────────────────
def generate_connector_table(model, out):
    lines = [f'# Connectors of {model.name}', '',
             '| ID | Source → Target | Nature | Coupling | Information carried | Boundary |',
             '|----|-----------------|--------|----------|---------------------|----------|']
    for k in _connectors(model):
        paths = '; '.join(' → '.join(c.label for c in link.path) for link in k.links)
        natures = ', '.join(NATURE[n] for n in k.natures).capitalize()
        lines.append(f'| {k.name} | {paths} | {natures} | {k.coupling.capitalize()} '
                     f'| {k.info} | {_boundary(k)} |')
    with open(os.path.join(out, 'connectors.md'), 'w') as f:
        f.write('\n'.join(lines) + '\n')


# ─────────────────────────────────────────────
# Model-to-text: graphical representation
# ─────────────────────────────────────────────
def _coordination(connector):
    """[F] A connector of coordination with other constituents: it crosses a boundary or
    passes through the anti-corruption layer. The rest are internal operation."""
    return any(_crosses(link) or any(c.translator for c in link.path) for link in connector.links)


def _view(model, connectors, name, out):
    """Laboratory 4 view, restricted to the given connectors and the components they join.
    [F] An edge written by several links of one connector (F-K23a ×3) is drawn once."""
    used = {c.name for k in connectors for link in k.links for c in link.path}
    lines = ['flowchart LR']
    for s in model.constituents:
        members = [c for c in _components(model) if c.system is s and c.name in used]
        if not members:
            continue
        lines.append(f'  subgraph {s.name}["{s.label}"]')
        for c in members:
            shape = f'[("{c.label} ({c.tier})")]' if c.tier == 'T4' else f'["{c.label} ({c.tier})"]'
            lines.append(f'    {c.name}{shape}')
        lines.append('  end')
    seen = set()
    for k in connectors:
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                if (a.name, b.name, k.name) not in seen:
                    seen.add((a.name, b.name, k.name))
                    lines.append(f'  {a.name} -->|{k.name}| {b.name}')
    with open(os.path.join(out, name), 'w') as f:
        f.write('\n'.join(lines) + '\n')


def generate_view(model, out):
    connectors = _connectors(model)
    _view(model, connectors, 'view.mmd', out)
    # [F] With an anti-corruption layer, two partial views separate the internal operation
    # (train control, track, services) from the coordination with other constituents.
    if any(c.translator for c in _components(model)):
        _view(model, [k for k in connectors if not _coordination(k)], 'view-operation.mmd', out)
        _view(model, [k for k in connectors if _coordination(k)], 'view-coordination.mmd', out)


# ─────────────────────────────────────────────
# Transformation to analysis: scenarios
# ─────────────────────────────────────────────
def _unavailability(factor):
    """Unavailability of a factor; a group of replicas uses the common-cause fraction beta."""
    if factor.__class__.__name__ == 'Single':
        return 1 - factor.ref.availability / 100, factor.ref.name
    u = 1 - factor.alternatives[0].ref.availability / 100
    b = factor.beta
    n = len(factor.alternatives)
    name = ', '.join(s.ref.name for s in factor.alternatives)
    return b * u + ((1 - b) * u) ** n, f'{name} (β = {b:g})'


def _base_latency(analysis):
    """Laboratory 4: a chain of single factors, each with its latency property."""
    return all(f.__class__.__name__ == 'Single' and not f.value and not f.unbounded
               and f.ref.latency for f in analysis.factors) and not analysis.percentile


def _stage(single, queue_exceedance):
    """[F] Latency of one stage in ms and its description. A queue takes the percentile left
    for it: -ln(e) x mean, with mean = 1 / (capacity - load) (A10)."""
    ref = single.ref
    if single.unbounded:
        return math.inf, 'unbounded'
    if single.value:
        return single.value, f'{single.value:g} ms (budget)'
    if ref.latency:
        return ref.latency, f'{ref.latency:g} ms'
    mean = 1000 / (ref.capacity - ref.load)
    if queue_exceedance is None:
        return mean, f'mean 1/({ref.capacity:g} − {ref.load:g}) = {mean:.1f} ms'
    k = -math.log(queue_exceedance / 100)
    return k * mean, (f'queue: mean 1/({ref.capacity:g} − {ref.load:g}) = {mean:.1f} ms; '
                      f'p{100 - queue_exceedance:g} = {k:.2f} × mean = {k * mean:.1f} ms')


def _general_latency(analysis):
    """[F] Sum of stages; a group runs in parallel and counts its maximum. With a percentile,
    each fixed stage (latency or budget) exceeds it in 0.1 % of the cases and the queues share
    what is left of 100 - percentile (Boole, A12)."""
    queue_exceedance = None
    if analysis.percentile:
        stages = [s for f in analysis.factors for s in singles(f)]
        fixed = sum(1 for s in stages if s.value or s.unbounded or s.ref.latency)
        queues = len(stages) - fixed
        if queues:
            queue_exceedance = ((100 - analysis.percentile) - fixed * FIXED_EXCEEDANCE) / queues
    rows, result = [], 0
    for f in analysis.factors:
        if f.__class__.__name__ == 'Group':
            stages = [(s.ref.name, *_stage(s, queue_exceedance)) for s in f.alternatives]
            value = max(v for _, v, _ in stages)
            names = ' ‖ '.join(f'{n} ({d})' for n, _, d in stages)
            shown = 'unbounded' if math.isinf(value) else f'{value:.1f} ms'
            rows.append(f'| {names} | {shown} (maximum, in parallel) |')
        else:
            value, description = _stage(f, queue_exceedance)
            rows.append(f'| {f.ref.name} | {description} |')
        result += value
    header = ['| Stage | Budget |', '|-------|--------|']
    label = f' p{analysis.percentile:g}' if analysis.percentile else ''
    shown = 'unbounded' if math.isinf(result) else f'{result:.0f} ms'
    summary = f'Chain latency{label}: **{shown}**'
    return header, rows, summary, result <= analysis.target


def analyze(analysis):
    rows = []
    if analysis.metric == 'availability':
        terms = [_unavailability(f) for f in analysis.factors]
        total_u = sum(u for u, _ in terms)
        result = 1.0
        for u, _ in terms:
            result *= 1 - u
        result *= 100
        for u, name in terms:
            rows.append(f'| {name} | {u * 100:.4f} % | {u / total_u * 100:.0f} % |')
        header = ['| Factor | Unavailability | Share |', '|--------|----------------|-------|']
        hours = (100 - result) / 100 * 8760
        summary = f'Chain availability: **{result:.2f} %** ({hours:.1f} h/year)'
        met = round(result, 6) >= analysis.target
    elif _base_latency(analysis):
        result = sum(f.ref.latency for f in analysis.factors)
        for f in analysis.factors:
            rows.append(f'| {f.ref.name} | {f.ref.latency:g} ms |')
        header = ['| Stage | Budget |', '|-------|--------|']
        summary = f'Chain latency: **{result:g} ms**'
        met = round(result, 6) <= analysis.target
    else:
        header, rows, summary, met = _general_latency(analysis)
    verdict = 'met' if met else 'NOT met'
    return [f'## {analysis.name} (Scenario {analysis.scenario})', ''] + header + rows + \
           ['', f'{summary}; target {analysis.target:g}: **{verdict}**', '']


def _silences(model):
    """[F] Supply connectors that feed an element of an availability chain and declare no
    period: their silence cannot be told apart from a failure of the source (Laboratory 2,
    section 4.2). Only internal connectors: global ones are governed by agreements."""
    critical = {s.ref.name for a in model.analyses if a.metric == 'availability'
                for f in a.factors for s in singles(f)}
    found = []
    for k in _connectors(model):
        if k.coupling != 'supply' or k.period or any(_crosses(link) for link in k.links):
            continue
        targets = sorted({link.path[-1].name for link in k.links} & critical)
        if targets:
            found.append(f'| {k.name} | {", ".join(targets)} | {k.info} |')
    if not found:
        return []
    return ['## Silent supply into availability chains', '',
            '| Connector | Feeds | Information carried |', '|-----------|-------|---------------------|'] + \
        found + ['']


def generate_analysis(model, out):
    lines = [f'# Analysis of {model.name}', '']
    for a in model.analyses:
        lines += analyze(a)
    lines += _silences(model)
    with open(os.path.join(out, 'analysis.md'), 'w') as f:
        f.write('\n'.join(lines))


def apply_transformations(model, out):
    os.makedirs(out, exist_ok=True)
    generate_connector_table(model, out)
    generate_view(model, out)
    generate_analysis(model, out)
