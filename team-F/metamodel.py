"""Metamodel of the language of team F (Rail): grammar arch.tx and constraints C1-C7, C12-C15.

Numbering of the constraints and its equivalence with the common language of Delivery 4
(common/metamodel.py, team D). C12-C16 keep the numbers of the common language so that the
teams converge; our C6 and C7 keep theirs, which in the common language name other rules.

| Ours | Common | Content | Origin |
|------|--------|---------|--------|
| C1-C4 | C1-C4 | Laboratory 4: links, single commander per command, agreement on boundary connectors, single user of a T4 store | Lab 4 |
| C5 | C5 | Properties that each analysis needs [F, extended]; in Delivery 4 also: `hit` in (0, 1] and only on a connector with capacity (and `vary hit` on such a connector, values in [0, 1]); in a workload, `Q reads S` only on a queue with its read dependency; a queue at most once per path; `drain` needs a store in the path of its workload and a fault | F |
| C6 | (C6 = layers, team D) | Hierarchical style of Rail: one commander per component, never up the tiers, no cycles | F (kept) |
| C7 | (C7 = no command crosses, team D; C8 [A] similar to ours) | Constituent gateway with anti-corruption layer | F (kept) |
| - | C9-C11 | Rules of teams A and C, scoped to CPS/RTS | not applicable |
| C12 | C12 (= Lab 5 C6) | Every hop of a workload follows a connector (either direction); with a fork, every pair (previous step, branch) and (branch, next step) | L5, adapted to forks [F] |
| C13 | C13 (= Lab 5 C7) | A fault only on a component with capacity | L5 |
| C14 | C14 | Six parts of a quality scenario; its measure is simulated (workloads, measures and run), verified_by an analysis, or not_verifiable | D4 (run is tested by replications: auto_init_attributes) |
| C15 | C15 | A tactic introduces or changes elements and its scenario is verified | D4 |
| C16 | C16 | Correspondence with sos.arch (K1-K3): correspondence.py --as RLS | D4 |

This metamodel keeps auto_init_attributes=True (textX default), so an optional number that is
not written takes 0, an optional string '' and an optional reference None; the checks test
truth values (e.g. `replications`, not `duration is None`). For that reason `hit` has the flag
`hit_set`: a connector with capacity and no `hit` written gets hit = 1 (assumption of E3).
"""
import os
from textx import metamodel_from_file, get_location, TextXSemanticError

SIX_PARTS = ('source', 'stimulus', 'artifact', 'environment', 'response')

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
    # [F] Only a component is a queue: the capacity of a connector is a read rate (A7).
    return element.__class__.__name__ == 'Component' and bool(element.capacity)


def reads(model, source, store):
    """[F] Blocking dependency connectors with a link from source to store."""
    return [k for k in model.elements if k.__class__.__name__ == 'Connector'
            and 'dependency' in k.natures and k.coupling == 'blocking'
            and any(link.path[0] is source and link.path[-1] is store for link in k.links)]


def _responses(model, source, store):
    """[F] Data flow connectors with a link from store back to source (the reply of the read)."""
    return [k for k in model.elements if k.__class__.__name__ == 'Connector'
            and 'data_flow' in k.natures
            and any(link.path[0] is store and link.path[-1] is source for link in k.links)]


def _check_read(model, where, queue, store, obj):
    """[F] C5. `Q reads S` (in an analysis or a workload): Q is a queue, a single blocking
    dependency Q -> S declares the read rate (capacity), and a data flow S -> Q carries the reply.
    Returns the dependency."""
    if not _is_queue(queue):
        _error(f'{where}: {queue.name} reads {store.name}: {queue.name} is not a queue', obj)
    rated = [k for k in reads(model, queue, store) if k.capacity]
    if not rated:
        _error(f'{where}: {queue.name} reads {store.name} through no blocking '
               f'dependency that declares capacity', obj)
    if len(rated) > 1:
        _error(f'{where}: {queue.name} reads {store.name}: several dependencies '
               f'with capacity {sorted(k.name for k in rated)}', obj)
    if not _responses(model, queue, store):
        _error(f'{where}: {queue.name} reads {store.name} with no data flow '
               f'{store.name} -> {queue.name} for the reply', obj)
    return rated[0]


def _cycle(graph):
    """A cycle of a directed graph {node: {next: ...}} as a list of nodes, or None."""
    done = set()

    def visit(node, path):
        for following in graph.get(node, {}):
            if following in path:
                return path[path.index(following):] + [following]
            if following not in done:
                found = visit(following, path + [following])
                if found:
                    return found
        done.add(node)
        return None

    for start in graph:
        found = None if start in done else visit(start, [start])
        if found:
            return found
    return None


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
        # C5 [F, as C]. misses counts periods: it needs a period (the grammar makes it a whole
        # number >= 1).
        if k.misses and not k.period:
            _error(f'{k.name}: misses needs a period', k)
        # C5 [F]. The capacity of a connector is the rate its source attains reading through
        # it, so it belongs to a blocking dependency only.
        if k.capacity and ('dependency' not in k.natures or k.coupling != 'blocking'):
            _error(f'{k.name}: capacity applies only to a blocking dependency', k)
        # C5 [F]. A read rate belongs to one path: a single link, so a single source, which is a
        # queue with a load below the rate (also when no analysis reads through it).
        if k.capacity:
            if len(k.links) != 1:
                _error(f'{k.name}: a connector with capacity needs a single link, '
                       f'it has {len(k.links)}', k)
            source = k.links[0].path[0]
            if not _is_queue(source) or not source.load:
                _error(f'{k.name}: the source {source.name} of a connector with capacity must be '
                       f'a queue with load', k)
            if k.capacity <= source.load:
                _error(f'{k.name}: capacity {k.capacity:g} is not above the load {source.load:g} '
                       f'of its source {source.name}', k)
        # C5 [F, Delivery 4]. hit is the fraction of the reads served at the capacity of the
        # dependency (cache hits): a fraction in (0, 1], only where there is such a capacity.
        if k.hit_set and not k.capacity:
            _error(f'{k.name}: hit applies only to a connector with capacity', k)
        if k.hit_set and not 0 < k.hit <= 1:
            _error(f'{k.name}: hit {k.hit:g} is not in (0, 1]', k)

    # C4. A data store (T4) is accessed by dependency from a single component.
    for c in components:
        if c.tier == 'T4':
            users = {link.path[-2].name
                     for k in connectors if 'dependency' in k.natures
                     for link in k.links if link.path[-1] is c}
            if len(users) > 1:
                _error(f'{c.name}: data store shared by {sorted(users)}', c)

    # C6 [F]. Hierarchical style of the Rail system (Delivery 1, section 5): authority flows
    # down from a single commander. Across all connectors (C2 checks one connector only):
    #   a) a component receives control commands from one source, also when it relays them;
    #   b) a command never goes up the tiers, from its source to its final target;
    #   c) control commands form no cycle.
    commands = [(k, link) for k in connectors if 'control_command' in k.natures for link in k.links]
    commanders, authority = {}, {}
    for k, link in commands:
        for c in link.path[1:]:
            commanders.setdefault(c.name, {}).setdefault(link.path[0].name, k)
            authority.setdefault(link.path[0].name, {}).setdefault(c.name, k)
    for target, sources in commanders.items():
        if len(sources) > 1:
            names = sorted(k.name for k in sources.values())
            _error(f'{target} receives control commands from several sources {sorted(sources)} '
                   f'through {names}', list(sources.values())[-1])
    for k, link in commands:
        source, target = link.path[0], link.path[-1]
        if target.tier < source.tier:
            _error(f'{k.name}: {source.name} ({source.tier}) commands {target.name} '
                   f'({target.tier}), up the tiers', k)
    cycle = _cycle(authority)
    if cycle:
        k = authority[cycle[-2]][cycle[-1]]
        _error(f'{k.name}: control commands form a cycle {" -> ".join(cycle)}', k)

    # C7 [F]. Constituent gateway with anti-corruption layer (Delivery 1, sections 4.3, 6 and 7):
    # in a constituent that declares a translator, a single component touches other
    # constituents, the gateway; it is not the translator, and every component of its own
    # constituent next to it on any link is the translator.
    with_translator = {c.system.name for c in components if c.translator}
    crossing = {}
    for k in connectors:
        for link in k.links:
            for a, b in zip(link.path, link.path[1:]):
                if a.system is not b.system:
                    for c in (a, b):
                        if c.system.name in with_translator:
                            crossing.setdefault(c.system.name, {}).setdefault(c.name, (c, k))
    gateways = set()
    for system, found in crossing.items():
        if len(found) > 1:
            _error(f'{system}: components {sorted(found)} cross its boundary; only its gateway may',
                   list(found.values())[-1][1])
        c, k = next(iter(found.values()))
        if c.translator:
            _error(f'{k.name}: the translator {c.name} crosses the boundary; only the gateway may', k)
        gateways.add(c.name)
    for k in connectors:
        for link in k.links:
            for i, c in enumerate(link.path):
                if c.name in gateways:
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
    #   a budget (= value or = unbounded) applies to latency and detection, percentile only to
    #   latency, and a budget counts as a fixed stage with the same 0.1 % of exceedance as a
    #   latency (A9).
    #   [F, as C] detection: a connector with period and misses (misses is required here, where
    #   the common language takes 1), a component with latency, or a budget.
    #   [F] `Q reads S`, only in latency and without budget: Q is a queue, a single blocking
    #   dependency Q -> S declares a capacity (above the load of Q, checked on the connector),
    #   and a data flow S -> Q carries the reply. It counts as a queue.
    for c in components:
        if _is_queue(c) and (c.latency or c.capacity <= c.load):
            _error(f'{c.name}: a queue needs a load below its capacity and no fixed latency', c)
    for a in model.analyses:
        if a.metric != 'latency' and a.percentile:
            _error(f'{a.name}: percentile applies only to latency', a)
        fixed, queues = 0, 0
        for f in a.factors:
            for s in singles(f):
                r = s.ref
                if s.store:
                    if a.metric != 'latency':
                        _error(f'{a.name}: reads applies only to latency', a)
                    if s.value or s.unbounded:
                        _error(f'{a.name}: {r.name} reads {s.store.name} takes no budget', a)
                    _check_read(model, a.name, r, s.store, a)
                    queues += 1
                    continue
                if a.metric == 'detection':
                    if s.value or s.unbounded:
                        continue
                    if r.__class__.__name__ == 'Connector':
                        if not (r.period and r.misses):
                            _error(f'{a.name}: {r.name} needs period and misses (or a budget)', a)
                    elif not r.latency:
                        _error(f'{a.name}: {r.name} has no latency property', a)
                    continue
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
            # Rounded: 100 - 99.9 is not exactly 0.1 in floating point.
            room = round((100 - a.percentile) - fixed * FIXED_EXCEEDANCE, 9)
            if room < 0 or (queues and room <= 0):
                _error(f'{a.name}: {fixed} fixed stages leave no exceedance for '
                       f'p{a.percentile:g}', a)

    check_scenarios(model, connectors)

    # [F] Not written, the hit fraction of a read dependency is 1 (assumption of Delivery 3).
    for k in connectors:
        if k.capacity and not k.hit_set:
            k.hit = 1.0


def _ends(step):
    """[F] The hops of a step of a workload: the branches of a fork, or the hop itself."""
    return step.branches if step.__class__.__name__ == 'Fork' else [step]


def _hops(workload):
    return [h for step in workload.steps for h in _ends(step)]


def check_scenarios(model, connectors):
    hops = {(a, b) for k in connectors for link in k.links for a, b in zip(link.path, link.path[1:])}
    for s in model.scenarios:
        for w in s.workloads:
            # C12 [L5 C6, F]. Every hop of a workload follows a connector of the model, in either
            # direction: the stimulus travels only along the declared structure. [F] With a fork,
            # every pair (previous step, branch) and (branch, next step).
            for prev, nxt in zip(w.steps, w.steps[1:]):
                for a in (h.ref for h in _ends(prev)):
                    for b in (h.ref for h in _ends(nxt)):
                        if (a, b) not in hops and (b, a) not in hops:
                            _error(f'{s.name}: {w.name} goes from {a.name} to {b.name} '
                                   f'without a connector', w)
            # C5 [F, Delivery 4]. In a path, `Q reads S` only on a queue with its read
            # dependency (as in an analysis), and a queue at most once: its jobs would otherwise
            # wait twice in the same FIFO and the hops could not tell its two visits apart.
            seen = set()
            for h in _hops(w):
                if h.store:
                    _check_read(model, f'{s.name}: {w.name}', h.ref, h.store, w)
                if _is_queue(h.ref):
                    if h.ref.name in seen:
                        _error(f'{s.name}: {w.name} goes through the queue {h.ref.name} more '
                               f'than once', w)
                    seen.add(h.ref.name)

        # C13 [L5 C7]. A component that fails in a scenario has a capacity.
        for f in s.faults:
            if not f.target.capacity:
                _error(f'{s.name}: fault on {f.target.name}, which has no capacity', f)

        # C5 [F, Delivery 4]. vary hit varies the hit fraction of a read dependency (values in
        # [0, 1]); a connector has no other parameter to vary.
        v = s.vary
        if v:
            is_connector = v.target.__class__.__name__ == 'Connector'
            if v.hit and not (is_connector and v.target.capacity):
                _error(f'{s.name}: vary hit on {v.target.name}, which is not a connector '
                       f'with capacity', v)
            if is_connector and not v.hit:
                _error(f'{s.name}: vary on the connector {v.target.name} needs hit', v)
            if v.hit and any(not 0 <= x <= 1 for x in v.values):
                _error(f'{s.name}: vary hit on {v.target.name} with values outside [0, 1]', v)

        # C14 [D4]. A quality scenario has its six parts: if it declares one of source,
        # stimulus, artifact, environment and response, it declares all of them, and its
        # response measure is verified in one of three ways: simulated (workloads, measures
        # and run), verified by an analysis of the model, or declared not verifiable with the
        # concept that is missing. [F] run is tested by replications (auto_init_attributes).
        declared = [p for p in SIX_PARTS if getattr(s, p)]
        if declared:
            missing = [p for p in SIX_PARTS if not getattr(s, p)]
            if missing:
                _error(f'{s.name}: quality scenario without {", ".join(missing)}', s)
        simulated = bool(s.workloads)
        if simulated and (not s.measures or not s.replications):
            _error(f'{s.name}: a simulated scenario needs at least one measure and its run', s)
        if s.measures and not simulated:
            _error(f'{s.name}: a measure needs a workload to measure', s)
        if declared and not (simulated or s.checks or s.missing):
            _error(f'{s.name}: the response measure is neither simulated, verified by an '
                   f'analysis, nor declared not verifiable', s)
        if s.missing and (simulated or s.checks):
            _error(f'{s.name}: declared not verifiable, but it is also verified', s)
        for m in s.measures:
            if m.workload and m.workload not in s.workloads:
                _error(f'{s.name}: measure on {m.workload.name}, a workload of another scenario', m)

        # C5 [F, Delivery 4]. drain measures how long the jobs that a store held take to leave
        # their path after the fault: it needs a fault and a store in the path of its workload
        # (without a workload, in the path of some workload of the scenario).
        for m in s.measures:
            if m.metric != 'drain':
                continue
            if not s.faults:
                _error(f'{s.name}: drain needs a fault in the scenario', m)
            measured = [m.workload] if m.workload else s.workloads
            if not any(h.ref.store for w in measured for h in _hops(w)):
                names = ', '.join(w.name for w in measured)
                _error(f'{s.name}: drain on {names}, whose path has no store', m)

    # C15 [D4]. A tactic is linked to what it changes and to a scenario whose measure is
    # verified, so its effect is verified, not assumed (Laboratory 5, section 6).
    for t in model.tactics:
        if not (t.introduces or t.changes):
            _error(f'{t.name}: tactic that introduces or changes no element', t)
        for s in t.scenarios:
            if s.missing or not (s.workloads or s.checks):
                _error(f'{t.name}: motivated by {s.name}, whose measure is not verified', t)


def create_metamodel():
    grammar = os.path.join(os.path.dirname(__file__), 'arch.tx')
    mm = metamodel_from_file(grammar)
    mm.register_obj_processors({'Misses': int})   # [F] the regex match is a string
    mm.register_model_processor(lambda model, metamodel: check_model(model))
    return mm
