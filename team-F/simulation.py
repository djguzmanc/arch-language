"""Step 4 of the verification process: simulation (Laboratory 5, section 4.3), team F (Rail).

Based on simulation.py of team D (common language, Delivery 4). The statistics and the API are
kept (T_975, interval, outcome, outcome_at_least, run_scenario, the Monte Carlo of availability);
the engine is rewritten as a discrete-event simulation with a heap, because the paths of team F
repeat a component (TRAD in rail-e1) and have forks, which the sweep by stations of D cannot run.

Semantics (Laboratory 5, section 2.3, and the marks of team D [D4] and of team F [F]):

  - Arrivals of each workload are Poisson with its rate, from 0 until the run ends; every job
    follows the steps of its workload and the run goes on until the last job leaves.
  - A component with capacity is a single FIFO server with exponential service at that rate [L5].
    [F] A hop `Q reads S` is served at the capacity of the read dependency Q -> S with
    probability hit (cache hit), and at the capacity of Q otherwise (hyperexponential service).
  - [F] A component with latency and no capacity adds its latency once per job (constant), as in
    the analysis of Delivery 3; a component with neither takes no time. The latency of a connector
    is added once per connector and job, when the job goes from one step to the next along it.
  - [F] A fork [A | B | C] runs its branches in parallel; the job goes on when the slowest ends.
    Each branch counts the constants that the job has not yet counted before the fork.
  - A fault is an interval in which the component serves nothing [L5]. A job that reaches it
    then is lost, unless the previous step is a store or [D4] the component is a store itself:
    then it is held until the fault ends. A job already waiting in its queue waits until the end.
  - Measures: p99_latency (ms, jobs that start after the warm-up and are not lost), lost (jobs
    that start after the warm-up), recovery (Laboratory 5 as in [D4]: from the end of the fault
    until the first new arrival finds no backlog, at the last queue of each workload) and [F]
    drain: from the end of the fault until the last job that a store held leaves its path.

Determinism: one random.Random(seed) per replication, seeds 1..n; the heap breaks ties by the
order in which the events were created. The Monte Carlo of availability uses seed 1000 + i.
"""
import heapq
import math
import random
import statistics

from textx import get_model

from metamodel import reads

# Student t quantiles (0.975) by degrees of freedom, for 95 % confidence intervals
T_975 = {1: 12.71, 2: 4.30, 3: 3.18, 4: 2.78, 5: 2.57, 6: 2.45, 7: 2.36, 8: 2.31,
         9: 2.26, 10: 2.23, 15: 2.13, 20: 2.09, 30: 2.04, 40: 2.02, 60: 2.00}

WITH_MARGIN = 'Satisfecha con margen'
WITHOUT_MARGIN = 'Satisfecha sin margen'
VIOLATED = 'Violada'
INCONCLUSIVE = 'Inconclusa'


def _kind(x):
    return x.__class__.__name__


def hops_of(step):
    """The hops of a step: the branches of a fork, or the hop itself."""
    return list(step.branches) if _kind(step) == 'Fork' else [step]


def hit_of(connector):
    """[F] Hit fraction of a read dependency; not written, 1 (assumption of Delivery 3)."""
    if getattr(connector, 'hit_set', False):
        return connector.hit
    return connector.hit or 1.0


def capacity_of(component):
    """Service rate of a component (requests or events per second), or None. [F] No instances:
    a replica in team F is an alternative of a group, which only availability counts."""
    return component.capacity or None


def read_connector(model, hop):
    """[F] The blocking dependency with capacity through which `Q reads S` reads."""
    found = [k for k in reads(model, hop.ref, hop.store) if k.capacity]
    return found[0] if found else None


def _connectors(model):
    return [e for e in model.elements if _kind(e) == 'Connector']


# ─────────────────────────────────────────────
# Transformation: static structure → dynamic structure (a plan per workload)
# ─────────────────────────────────────────────

class Branch:
    """One hop of a step, with what the job adds around it (in seconds)."""
    __slots__ = ('name', 'queue', 'mu', 'read', 'store', 'prev_store', 'pre', 'const', 'post',
                 'pre_connectors', 'post_connectors', 'constant')

    def __init__(self, hop):
        c = hop.ref
        self.name, self.queue, self.store = c.name, bool(capacity_of(c)), bool(c.store)
        self.mu = capacity_of(c)
        self.read = None                    # (connector name, capacity) of `Q reads S`
        self.prev_store = False
        self.pre = self.const = self.post = 0.0
        self.pre_connectors, self.post_connectors, self.constant = [], [], None


def _pairs(steps):
    """Every (a, b) of consecutive steps: with a fork, (previous, branch) and (branch, next)."""
    out = set()
    for prev, nxt in zip(steps, steps[1:]):
        for a in hops_of(prev):
            for b in hops_of(nxt):
                out.add((a.ref.name, b.ref.name))
    return out


def connector_between(model, a, b, pairs):
    """[F] The connector that a job follows from a to b (C12: a link where they are consecutive,
    in either direction). If several connectors join them, the one whose link shares more
    consecutive pairs with the workload; then the forward direction; then the first declared."""
    best, key = None, None
    for i, k in enumerate(_connectors(model)):
        for link in k.links:
            names = [c.name for c in link.path]
            steps = list(zip(names, names[1:]))
            if (a, b) in steps:
                forward = 1
            elif (b, a) in steps:
                forward = 0
            else:
                continue
            shared = sum(1 for p in steps if p in pairs or (p[1], p[0]) in pairs)
            candidate = (shared, forward, -i)
            if key is None or candidate > key:
                best, key = k, candidate
    return best


def build_plan(model, steps):
    """Plan of a path: a list of steps, each a list of Branch. Works on the steps of a workload
    or on any list of objects with ref/store (hops) or branches (forks)."""
    pairs = _pairs(steps)
    seen_components, seen_connectors = set(), set()
    plan = []
    previous = None
    for i, step in enumerate(steps):
        fork = _kind(step) == 'Fork'
        branches = []
        new_components, new_connectors = set(), set()
        for hop in hops_of(step):
            b = Branch(hop)
            if getattr(hop, 'store', None):
                k = read_connector(model, hop)
                if k is not None:
                    b.read = (k.name, k.capacity)
            if previous is not None:
                b.prev_store = any(h.ref.store for h in hops_of(previous))
                # the connector from the previous step, unless the previous step is a fork
                # (then each of its branches counted it on its way out)
                if _kind(previous) != 'Fork':
                    k = connector_between(model, previous.ref.name, b.name, pairs)
                    if k is not None and k.latency and k.name not in seen_connectors:
                        b.pre, b.pre_connectors = k.latency / 1000.0, [k.name]
            c = hop.ref
            if not b.queue and c.latency and c.name not in seen_components:
                b.const, b.constant = c.latency / 1000.0, c.name
            if fork and i + 1 < len(steps):
                for nxt in hops_of(steps[i + 1]):
                    k = connector_between(model, b.name, nxt.ref.name, pairs)
                    if k is not None and k.latency and k.name not in seen_connectors \
                            and k.name not in b.post_connectors:
                        b.post += k.latency / 1000.0
                        b.post_connectors.append(k.name)
            new_components.add(c.name)
            new_connectors |= set(b.pre_connectors) | set(b.post_connectors)
            branches.append(b)
        # each branch of a fork counts what the job had not counted before the fork
        seen_components |= new_components
        seen_connectors |= new_connectors
        plan.append(branches)
        previous = step
    return plan


# ─────────────────────────────────────────────
# Execution of one replication
# ─────────────────────────────────────────────

class Result:
    """What one replication leaves for the measures, per workload."""

    def __init__(self, names):
        self.latencies = {n: [] for n in names}     # seconds, jobs after the warm-up, not lost
        self.lost = {n: 0 for n in names}            # jobs after the warm-up
        self.held = {n: 0 for n in names}            # jobs held by a store
        self.held_end = {n: None for n in names}     # time the last held job left its path
        self.recovered = {}                          # queue -> recovery time (s)
        self.end_of_fault = None
        self.duration = 0.0


def simulate(scenario, seed, rates, capacities, hits=None, plans=None):
    """
    One replication of the scenario. rates: workload -> rate; capacities: component -> rate;
    hits: read connector -> hit fraction (default: the model's); plans: workload -> plan
    (default: build_plan of its steps). Returns a Result.
    """
    model = get_model(scenario)
    rng = random.Random(seed)
    expo, rand = rng.expovariate, rng.random
    hits = dict(hits or {})
    for k in _connectors(model):
        if k.capacity and k.name not in hits:
            hits[k.name] = hit_of(k)
    workloads = list(scenario.workloads)
    names = [w.name for w in workloads]
    plans = plans or {w.name: build_plan(model, w.steps) for w in workloads}
    down = {}
    for f in scenario.faults:
        down.setdefault(f.target.name, []).append((f.start, f.start + f.length))
    end_of_fault = max((d1 for ivs in down.values() for _, d1 in ivs), default=None)
    duration, warmup = scenario.duration, scenario.warmup
    res = Result(names)
    res.end_of_fault, res.duration = end_of_fault, duration
    free = {}
    recovered = res.recovered

    def down_until(name, t):
        for d0, d1 in down.get(name, ()):
            if d0 <= t < d1:
                return d1
        return None

    def serve(b, ta, held):
        """FIFO single server: arrival at ta, returns the departure."""
        mu = capacities.get(b.name, b.mu)
        if b.read is not None and rand() < hits[b.read[0]]:
            mu = b.read[1]
        f = free.get(b.name, 0.0)
        if end_of_fault is not None and b.name not in recovered and not held \
                and ta > end_of_fault and ta >= f:
            recovered[b.name] = ta - end_of_fault   # first new arrival that finds no backlog
        start = ta if ta > f else f
        d1 = down_until(b.name, start)
        if d1 is not None:
            start = d1                              # the server does not work while down
        f = start + expo(mu)
        free[b.name] = f
        return f

    heap = []
    seq = 0
    # job: [workload index, start, held]
    plan_list = [plans[n] for n in names]

    def finish(job, t):
        w = names[job[0]]
        if job[2]:
            res.held[w] += 1
            if res.held_end[w] is None or t > res.held_end[w]:
                res.held_end[w] = t
        if job[1] >= warmup:
            res.latencies[w].append(t - job[1])

    def lose(job):
        if job[1] >= warmup:
            res.lost[names[job[0]]] += 1

    def advance(job, i, t, now, arrived):
        """Runs the job from step i. t: time it is ready for step i, or, if arrived, the time
        it reaches the queue of step i. Queues are served only in time order: a job that
        reaches a queue after now waits in the heap."""
        nonlocal seq
        plan = plan_list[job[0]]
        n = len(plan)
        while i < n:
            branches = plan[i]
            if not arrived:
                ta_queue = min((t + b.pre for b in branches if b.queue), default=None)
                if ta_queue is not None and ta_queue > now:
                    heapq.heappush(heap, (ta_queue, seq, job, i, t))
                    seq += 1
                    return
            # faults first: a branch that is lost loses the job, one that is held holds it
            hold = None
            for b in branches:
                ta = t + b.pre
                d1 = down_until(b.name, ta)
                if d1 is not None:
                    if b.store or b.prev_store:
                        hold = d1 if hold is None or d1 > hold else hold
                    else:
                        lose(job)
                        return
            if hold is not None:
                job[2] = True
                # ready again at the end of the fault, with the connector already crossed
                heapq.heappush(heap, (hold, seq, job, i, hold - max(b.pre for b in branches)))
                seq += 1
                return
            done = t
            for b in branches:
                ta = t + b.pre
                f = serve(b, ta, job[2]) if b.queue else ta
                f += b.const + b.post
                if f > done:
                    done = f
            t, i, arrived = done, i + 1, False
        finish(job, t)

    nexts = []
    for w in workloads:
        rate = rates[w.name]
        nexts.append(expo(rate) if rate > 0 else math.inf)
    while True:
        k, na = -1, math.inf
        for idx, v in enumerate(nexts):
            if v < na:
                k, na = idx, v
        if na >= duration:
            na = math.inf
        if heap and heap[0][0] <= na:
            ta, _, job, i, t = heapq.heappop(heap)
            advance(job, i, t, ta, True)
        elif na < math.inf:
            rate = rates[names[k]]
            nexts[k] = na + expo(rate)
            advance([k, na, False], 0, na, na, False)
        else:
            break
    if end_of_fault is not None:
        for p in plan_list:
            for s in p:
                for b in s:
                    if b.queue:
                        recovered.setdefault(b.name, max(duration - end_of_fault, 0.0))
    return res


def _recovery(scenario, res, workload=None):
    """Laboratory 5, as in [D4]: at the last queue of each workload; the slowest one when the
    measure names no workload."""
    if res.end_of_fault is None:
        return 0.0
    model = get_model(scenario)
    workloads = [workload] if workload else scenario.workloads
    times = []
    for w in workloads:
        queues = [b.name for s in build_plan(model, w.steps) for b in s if b.queue
                  and b.name in res.recovered]
        if queues:
            times.append(res.recovered[queues[-1]])
    return max(times, default=0.0)


def _drain(scenario, res, workload=None):
    """[F] From the end of the fault until the last job that a store held leaves its path."""
    if res.end_of_fault is None:
        return 0.0
    names = [workload.name] if workload else [w.name for w in scenario.workloads]
    ends = [res.held_end[n] for n in names if res.held_end[n] is not None]
    return max(ends) - res.end_of_fault if ends else 0.0


def _scale(value_s, unit):
    return value_s * 1000.0 if unit == 'ms' else value_s


def _measure(m, scenario, res):
    if m.metric == 'lost':
        names = [m.workload.name] if m.workload else [w.name for w in scenario.workloads]
        return float(sum(res.lost[n] for n in names))
    if m.metric == 'recovery':
        return _scale(_recovery(scenario, res, m.workload), m.unit)
    if m.metric == 'drain':
        return _scale(_drain(scenario, res, m.workload), m.unit)
    names = [m.workload.name] if m.workload else [w.name for w in scenario.workloads]
    times = sorted(t for n in names for t in res.latencies[n])
    if not times:
        return math.nan
    return _scale(times[max(0, math.ceil(0.99 * len(times)) - 1)], m.unit)


# ─────────────────────────────────────────────
# Replications, confidence intervals, and outcome (team D, unchanged except the labels)
# ─────────────────────────────────────────────

def interval(values):
    mean = statistics.mean(values)
    if len(values) < 2:
        return mean, mean, mean
    df = len(values) - 1
    t = T_975[max(k for k in T_975 if k <= df)]
    half = t * statistics.stdev(values) / math.sqrt(len(values))
    return mean, mean - half, mean + half


def outcome(low, high, threshold):
    """Classification of Unit 6, Reading 2, §4.1, with a margin of 10 % of the threshold."""
    if high <= 0.9 * threshold:
        return WITH_MARGIN
    if high <= threshold:
        return WITHOUT_MARGIN
    if low > threshold:
        return VIOLATED
    return INCONCLUSIVE


def outcome_at_least(low, high, threshold, margin):
    """[D4] The same classification for a measure that must be at least the threshold; the
    margin is absolute, in the unit of the threshold."""
    if low >= threshold + margin:
        return WITH_MARGIN
    if low >= threshold:
        return WITHOUT_MARGIN
    if high < threshold:
        return VIOLATED
    return INCONCLUSIVE


def availability_margin(threshold):
    """[F] Margin of an availability: 10 % of the unavailability allowed (the rule of 10 % of
    Laboratory 5 applied to the measure, unavailability). 99.95 % → 0.005 pp: with margin from
    99.955 %. Team D uses 0.02 pp absolute."""
    return 0.1 * (100.0 - threshold)


def outcome_availability(low, high, threshold):
    """[F] With margin if the unfavourable end of the CI ≥ 100 − 0.9·(100 − threshold)."""
    return outcome_at_least(low, high, threshold, availability_margin(threshold))


def scenario_point(scenario, value):
    """rates, capacities and hits of the scenario for one value of its varied parameter."""
    model = get_model(scenario)
    rates = {w.name: w.rate for w in scenario.workloads}
    capacities = {}
    for w in scenario.workloads:
        for step in w.steps:
            for h in hops_of(step):
                if capacity_of(h.ref):
                    capacities[h.ref.name] = capacity_of(h.ref)
    hits = {k.name: hit_of(k) for k in _connectors(model) if k.capacity}
    v = scenario.vary
    if v is not None and value is not None:
        target = v.target
        if _kind(target) == 'Workload':
            rates[target.name] = value
        elif _kind(target) == 'Component':
            capacities[target.name] = value
        else:                                       # [F] vary hit K
            hits[target.name] = value
    return rates, capacities, hits


def model_value(scenario):
    """The value that the model itself gives to the varied parameter (None if no vary)."""
    v = scenario.vary
    if v is None:
        return None
    t = v.target
    if _kind(t) == 'Workload':
        return t.rate
    if _kind(t) == 'Component':
        return t.capacity
    return hit_of(t)


def run_point(scenario, value=None, replications=None, plans=None, hits=None):
    """Replications 1..n of one value of the varied parameter: {measure: [values]}."""
    rates, capacities, h = scenario_point(scenario, value)
    if hits:
        h.update(hits)
    n = replications or scenario.replications
    samples = {m: [] for m in scenario.measures}
    for seed in range(1, n + 1):
        res = simulate(scenario, seed, rates, capacities, h, plans)
        for m in scenario.measures:
            samples[m].append(_measure(m, scenario, res))
    return samples


def run_scenario(scenario, values=None, replications=None, plans=None, hits=None):
    """Runs every value of the varied parameter, with independent replications (seeds 1..n).
    Returns (value, measure, mean, low, high, outcome) as team D."""
    if values is None:
        values = list(scenario.vary.values) if scenario.vary else [None]
    results = []
    for value in values:
        samples = run_point(scenario, value, replications, plans, hits)
        for m in scenario.measures:
            mean, low, high = interval(samples[m])
            results.append((value, m, mean, low, high, outcome(low, high, m.threshold)))
    return results


# ─────────────────────────────────────────────
# [F] Known results (Laboratory 5, section 4.6) for the check of the simulator
# ─────────────────────────────────────────────

def _queue_rate(scenario, name, rates):
    """Arrival rate at a queue: the rates of the workloads whose path goes through it."""
    total = 0.0
    for w in scenario.workloads:
        visits = sum(1 for s in w.steps for h in hops_of(s) if h.ref.name == name)
        total += visits * rates[w.name]
    return total


def known_result(scenario, m, value=None):
    """Closed-form value of a measure, in its unit, when the path allows it, with the formula
    used; else (None, reason). Cases:
      - p99_latency of a workload with a single M/M/1 queue (no fault; a read with hit 0 or 1):
        ln(100)/(μ − λ) plus the constants of the path (in a fork, the slowest branch);
      - drain with one fault on a queue, held by a store: E[N]/μ + constants after the queue,
        E[N] = λ·length (the last held job leaves after N services); and the backlog formula of
        Laboratory 5, E[N]/(μ − λ), as a second reference;
      - lost: 0 if a store holds the jobs, else λ·length (expected).
    """
    model = get_model(scenario)
    rates, capacities, hits = scenario_point(scenario, value)
    if m.workload is None and len(scenario.workloads) != 1:
        return None, 'medida sin workload'
    w = m.workload or scenario.workloads[0]
    plan = build_plan(model, w.steps)
    queues = [(i, b) for i, s in enumerate(plan) for b in s if b.queue]
    if m.metric == 'p99_latency':
        if scenario.faults:
            return None, 'con falla'
        if len(queues) != 1:
            return None, f'{len(queues)} colas en el camino'
        _, q = queues[0]
        mu = capacities.get(q.name, q.mu)
        if q.read is not None:
            h = hits[q.read[0]]
            if h == 1:
                mu = q.read[1]
            elif h != 0:
                return None, 'servicio hiperexponencial (0 < hit < 1)'
        lam = _queue_rate(scenario, q.name, rates)
        if lam >= mu:
            return None, 'cola inestable (λ ≥ μ)'
        total = 0.0
        for s in plan:
            total += max((math.log(100) / (mu - lam) if b.queue else 0.0) + b.pre + b.const + b.post
                         for b in s)
        formula = f'ln(100)/({mu:g} − {lam:g}) + constantes'
        return {'value': _scale(total, m.unit), 'formula': formula}, None
    if m.metric in ('drain', 'recovery'):
        if len(scenario.faults) != 1:
            return None, 'se necesita una falla'
        f = scenario.faults[0]
        hit = [(i, b) for i, b in queues if b.name == f.target.name]
        if not hit:
            return None, 'la falla no está en una cola del camino'
        i, q = hit[0]
        if not (q.store or q.prev_store):
            return None, 'sin store: los trabajos se pierden'
        mu = capacities.get(q.name, q.mu)
        lam = _queue_rate(scenario, q.name, rates)
        n = rates[w.name] * f.length
        after = sum(max(b.pre + b.const + b.post + (0 if b.queue else 0) for b in s)
                    for s in plan[i + 1:]) + q.const + q.post
        if any(b.queue for s in plan[i + 1:] for b in s):
            return None, 'otra cola después de la falla'
        last_held = n / mu + after
        busy = n / (mu - lam) + after if lam < mu else math.inf
        if m.metric == 'drain':
            return {'value': _scale(last_held, m.unit),
                    'formula': f'E[N]/μ = {n:g}/{mu:g} + constantes',
                    'second': _scale(busy, m.unit),
                    'second_formula': f'E[N]/(μ − λ) = {n:g}/({mu:g} − {lam:g}) (L5)'}, None
        return {'value': _scale(busy, m.unit),
                'formula': f'backlog/(μ − λ) = {n:g}/({mu:g} − {lam:g})'}, None
    if m.metric == 'lost':
        if not scenario.faults:
            return {'value': 0.0, 'formula': 'sin falla'}, None
        total = 0.0
        for f in scenario.faults:
            for i, s in enumerate(plan):
                for b in s:
                    if b.name == f.target.name and not (b.store or b.prev_store):
                        total += rates[w.name] * f.length
        return {'value': total, 'formula': 'store retiene: 0' if total == 0 else 'λ·duración'}, None
    return None, 'sin fórmula'


# ─────────────────────────────────────────────
# [D4, adapted] Availability: Monte Carlo of failures and repairs
# ─────────────────────────────────────────────
# Each factor of an availability analysis fails and is repaired as an alternating renewal
# process with availability A and mean time to repair MTTR. [F] A group of n alternatives is
# down when all of them are down: each fails independently at rate (1 − β)·λ, and a
# common-cause shock at rate β·λ takes all of them down (Laboratory 3). No instances/replicas.

MTTR_HOURS = 4.0        # assumption (as team D): the model declares no repair time
AVAILABILITY_SEED = 1000


def _downs(rng, rate, mttr, horizon):
    t, out = 0.0, []
    while rate > 0:
        t += rng.expovariate(rate)
        if t >= horizon:
            break
        d = rng.expovariate(1.0 / mttr)
        out.append((t, min(t + d, horizon)))
        t += d
    return out


def _intersect(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        s, e = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if s < e:
            out.append((s, e))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def _union(intervals):
    total, cs, ce = 0.0, None, None
    for s, e in sorted(intervals):
        if ce is None or s > ce:
            if ce is not None:
                total += ce - cs
            cs, ce = s, e
        else:
            ce = max(ce, e)
    return total + (ce - cs if ce is not None else 0.0)


def availability_factors(analysis):
    """[F] (availability %, alternatives, beta) of each factor, read from the model."""
    out = []
    for f in analysis.factors:
        if _kind(f) == 'Group':
            a = min(s.ref.availability for s in f.alternatives)
            out.append((a, len(f.alternatives), f.beta or 0.0))
        else:
            out.append((f.ref.availability, 1, 0.0))
    return out


def analytic_availability(factors):
    """Laboratory 3: a group of n with common cause: β·u + ((1 − β)·u)^n."""
    a = 1.0
    for av, n, b in factors:
        u = 1 - av / 100.0
        a *= 1 - (b * u + ((1 - b) * u) ** n if n > 1 else u)
    return 100 * a


def simulate_factors(factors, seed, years=20, replications=40, mttr=MTTR_HOURS):
    horizon = years * 8760.0
    rng = random.Random(seed)
    values = []
    for _ in range(replications):
        downs = []
        for av, n, b in factors:
            u = 1 - av / 100.0
            lam = u / ((1 - u) * mttr)
            if n == 1:
                downs += _downs(rng, lam, mttr, horizon)
                continue
            both = _downs(rng, (1 - b) * lam, mttr, horizon)
            for _ in range(n - 1):
                both = _intersect(both, _downs(rng, (1 - b) * lam, mttr, horizon))
            downs += both + _downs(rng, b * lam, mttr, horizon)
        values.append(100.0 * (1 - _union(downs) / horizon))
    return values


def simulate_availability(analysis, seed, years=20, replications=40, beta=None, mttr=MTTR_HOURS):
    """Monte Carlo of the analysis; returns (values %, Lab 3 formula %)."""
    factors = availability_factors(analysis)
    if beta is not None:
        factors = [(a, n, beta if n > 1 else b) for a, n, b in factors]
    return simulate_factors(factors, seed, years, replications, mttr), analytic_availability(factors)
