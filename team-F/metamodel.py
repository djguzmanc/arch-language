import os
from textx import metamodel_from_file, get_location, TextXSemanticError

FIXED_EXCEEDANCE = 0.1   # % of cases in which a fixed stage exceeds its budget (A9: p99.9)


def _error(message, obj):
    raise TextXSemanticError(message, **get_location(obj))


def _crosses(link):
    return len({c.system.name for c in link.path}) > 1


def _boundary(connector):
    """A connector is a boundary connector when one of its links joins two constituents."""
    return any(_crosses(link) for link in connector.links)


def singles(factor):
    """The single factors of a factor: itself, or the members of a group."""
    return factor.alternatives if factor.__class__.__name__ == 'Group' else [factor]


def _is_queue(element):
    return bool(getattr(element, 'capacity', 0))


def check_model(model):
    components = [e for e in model.elements if e.__class__.__name__ == 'Component']
    connectors = [e for e in model.elements if e.__class__.__name__ == 'Connector']

    for k in connectors:
        # C1. Every link joins at least two components.
        for link in k.links:
            if len(link.path) < 2:
                _error(f'{k.name}: a link must join at least two components', k)
        # C2. A control command has a single source with authority over its targets.
        if 'control_command' in k.natures:
            sources = {link.path[0].name for link in k.links}
            if len(sources) > 1:
                _error(f'{k.name}: control command with several sources {sorted(sources)}', k)
        # C3. Every boundary connector is governed by an agreement among owners.
        if _boundary(k) and not k.agreement:
            _error(f'{k.name}: boundary connector without agreement', k)

    # C4. A data store (T4) is accessed by dependency from a single component.
    for c in components:
        if c.tier == 'T4':
            users = {link.path[-2].name
                     for k in connectors if 'dependency' in k.natures
                     for link in k.links if link.path[-1] is c}
            if len(users) > 1:
                _error(f'{c.name}: data store shared by {sorted(users)}', c)

    # C6 [F]. Hierarchical style of the Rail system (Delivery 1, section 5): authority flows
    # down from a single commander. Every component receives control commands from one source
    # only, across all connectors (C2 checks it within one connector).
    commanders = {}
    for k in connectors:
        if 'control_command' in k.natures:
            for link in k.links:
                commanders.setdefault(link.path[-1].name, {}).setdefault(link.path[0].name, k)
    for target, sources in commanders.items():
        if len(sources) > 1:
            names = sorted(k.name for k in sources.values())
            _error(f'{target} receives control commands from several sources {sorted(sources)} '
                   f'through {names}', list(sources.values())[-1])

    # C7 [F]. Constituent gateway with anti-corruption layer (Delivery 1, sections 4.3 and 6):
    # in a constituent that declares a translator, the gateway is the component that touches
    # another constituent, and every component of its own constituent next to it on any link
    # is the translator.
    with_translator = {c.system.name for c in components if c.translator}
    gateways = set()
    for k in connectors:
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                if a.system is not b.system:
                    gateways.update({a.name, b.name})
    for k in connectors:
        for link in k.links:
            for i, c in enumerate(link.path):
                if c.name in gateways and c.system.name in with_translator and not c.translator:
                    neighbours = link.path[max(i - 1, 0):i] + link.path[i + 1:i + 2]
                    for n in neighbours:
                        if n.system is c.system and not n.translator:
                            _error(f'{k.name}: {n.name} reaches the gateway {c.name} '
                                   f'without the translator', k)

    # C5 [F, extended]. Every factor of an analysis carries what the analysis needs
    # (an optional number that is not written takes the value 0):
    #   availability: the availability property;
    #   latency: a latency, a budget (= value) or, as a queue, capacity above its load;
    #   percentile: the exceedance of the fixed stages leaves room for the queues (Boole, A12).
    #   a budget (= value or = unbounded) and percentile only apply to latency, and a budget
    #   counts as a fixed stage with the same 0.1 % of exceedance as a latency (A9).
    for c in components:
        if _is_queue(c) and (c.latency or c.capacity <= c.load):
            _error(f'{c.name}: a queue needs a load below its capacity and no fixed latency', c)
    for a in model.analyses:
        if a.metric == 'availability' and a.percentile:
            _error(f'{a.name}: percentile applies only to latency', a)
        fixed, queues = 0, 0
        for f in a.factors:
            for s in singles(f):
                r = s.ref
                if a.metric == 'availability':
                    if s.value or s.unbounded:
                        _error(f'{a.name}: a budget (= value) applies only to latency', a)
                    if not r.availability:
                        _error(f'{a.name}: {r.name} has no availability property', a)
                    continue
                if s.value or s.unbounded or r.latency:
                    fixed += 1
                elif _is_queue(r):
                    queues += 1
                else:
                    _error(f'{a.name}: {r.name} has no latency property', a)
            if a.metric == 'availability' and f.__class__.__name__ == 'Group' and \
                    len({s.ref.availability for s in f.alternatives}) > 1:
                _error(f'{a.name}: replicas {[s.ref.name for s in f.alternatives]} '
                       f'have different availability', a)
        if a.metric == 'latency' and queues and not a.percentile:
            _error(f'{a.name}: a chain with queues needs a percentile', a)
        if a.percentile:
            room = (100 - a.percentile) - fixed * FIXED_EXCEEDANCE
            if room < 0 or (queues and room <= 0):
                _error(f'{a.name}: {fixed} fixed stages leave no exceedance for '
                       f'p{a.percentile:g}', a)


def create_metamodel():
    grammar = os.path.join(os.path.dirname(__file__), 'arch.tx')
    mm = metamodel_from_file(grammar)
    mm.register_model_processor(lambda model, metamodel: check_model(model))
    return mm
