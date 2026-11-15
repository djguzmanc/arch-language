"""Justification of the tactics (Delivery 4, iterations 2 and 4), team F (Rail).

As tactics_check.py of team D, with the simulators of simulation.py:
  1. contribution of each tactic of Delivery 2 to P1 (F-QS7, p99 of the capacity request) in
     rail-e2: with and without the cache (hit 1 / hit 0) and with and without the parallel calls
     (fork / the sequential path of rail-e1), with the known result of each variant;
  2. contribution of T4.1 to P7 (F-QS5 with the track) in rail-e4: neither (rail-e3), only CONB,
     only ILKB, both; Monte Carlo with the Lab 3 formula as known result;
  3. sensitivity of P7 to the common-cause fraction beta in rail-e4, and the beta at which the
     formula crosses the threshold and the threshold with margin.

Usage: python3 tactics_check.py      (writes out/tactics/tactics.md)
"""
import os

from metamodel import create_metamodel
from verification import MC_REPLICATIONS, MC_YEARS, check_availability
from simulation import (MTTR_HOURS, analytic_availability, availability_factors,
                        availability_margin, build_plan, interval, known_result, outcome,
                        outcome_availability, run_point, simulate_factors)


BETAS = [0.0, 0.02, 0.05, 0.08, 0.10, 0.12, 0.15, 0.20]


def _by_name(items, name):
    return next(x for x in items if x.name == name)


def serialize(steps):
    """[F] The path without parallel calls, derived from the fork of the model: the branches run
    one after the other, each reply coming back through the step after the fork, from which the
    next call leaves: P -> [B1 | ... | Bk] -> N becomes P -> B1 -> N -> B2 -> N -> ... -> Bk -> N.
    With P = N = TRAD this is the path of rail-e1."""
    out = []
    for i, step in enumerate(steps):
        if step.__class__.__name__ != 'Fork':
            out.append(step)
            continue
        if i + 1 >= len(steps):
            raise ValueError('a fork at the end of the path has no step to come back through')
        back = steps[i + 1]
        for j, branch in enumerate(step.branches):
            out.append(branch)
            if j < len(step.branches) - 1:
                out.append(back)
    return out


def _path(steps):
    return ' → '.join(h.ref.name + (f' reads {h.store.name}' if h.store else '') for h in steps)


def contribution_p1(mm, lines):
    e2 = mm.model_from_file('models/rail-e2.arch')
    s = _by_name(e2.scenarios, 'QS_F7')
    m = s.measures[0]
    w = s.workloads[0]
    serial = serialize(list(w.steps))
    plans_seq = {w.name: build_plan(e2, serial)}
    variants = [('rail-e2: caché + paralelo (hit 1)', 1.0, None),
                ('sin caché (hit 0), con paralelo', 0.0, None),
                ('con caché (hit 1), sin paralelo (camino en serie)', 1.0, plans_seq),
                ('sin caché ni paralelo (≈ rail-e1)', 0.0, plans_seq)]
    lines += ['## 1. Contribución de cada táctica de la Entrega 2 a P1 (F-QS7, rail-e2)', '',
              f'{s.replications} réplicas (semillas 1–{s.replications}), corrida {s.duration:g} s, '
              f'calentamiento {s.warmup:g} s; umbral ≤ {m.threshold:g} ms. Sin caché = hit 0 en '
              f'{s.vary.target.name if s.vary else "el conector de lectura"}. Sin paralelo = las '
              f'ramas del fork del modelo en serie: {_path(serial)}. El resultado conocido sale de '
              'known_result sobre el plan de cada variante (una cola M/M/1 más las constantes).', '',
              '| Estructura | Estimación | IC 95 % | Conocido | ¿Dentro? | Resultado |',
              '|---|---|---|---|---|---|']
    for label, hit, plans in variants:
        samples = run_point(s, hit, plans=plans)[m]
        mean, low, high = interval(samples)
        k, why = known_result(s, m, hit, plans=plans)
        known = k['value'] if k else None
        inside = '—' if known is None else ('sí' if low <= known <= high else 'no')
        lines.append(f'| {label} | {mean:.1f} ms | [{low:.1f}; {high:.1f}] | '
                     f'{why if known is None else f"{known:.1f} ms"} | {inside} | '
                     f'{outcome(low, high, m.threshold)} |')
    lines.append('')


def _mc(factors, seed, target):
    values = simulate_factors(factors, seed, MC_YEARS, MC_REPLICATIONS, MTTR_HOURS)
    mean, low, high = interval(values)
    exact = analytic_availability(factors)
    return mean, low, high, exact, outcome_availability(low, high, target)


def contribution_t41(mm, lines):
    e4 = mm.model_from_file('models/rail-e4.arch')
    a = _by_name(e4.analyses, 'FQS5WithTrack')
    names = [[s.ref.name for s in (f.alternatives if f.__class__.__name__ == 'Group' else [f])]
             for f in a.factors]
    full = availability_factors(a)

    def without(primary):
        """The factor whose group contains primary, back to the single primary of rail-e3."""
        out = []
        for group, factor in zip(names, full):
            if primary in group:
                c = _by_name(e4.elements, primary)
                out.append((c.availability, 1, 0.0))
            else:
                out.append(factor)
        return out

    # the seed that verification.py gives to FQS5WithTrack in out/rail-e4
    seed = next(row[2] for row in check_availability(e4) if row[1].name == a.name)
    neither = without('ILK')
    neither = [(_by_name(e4.elements, 'CON').availability, 1, 0.0) if 'CON' in g else f
               for f, g in zip(neither, names)]
    variants = [('rail-e3: sin T4.1 (ILK y CON únicos)', neither),
                ('solo CONB (ILK único)', without('ILK')),
                ('solo ILKB (CON único)', without('CON')),
                ('rail-e4: CONB + ILKB (T4.1)', full)]
    lines += ['## 2. Contribución de T4.1 a P7 (F-QS5 con vía, rail-e4)', '',
              f'Monte Carlo {MC_REPLICATIONS} réplicas × {MC_YEARS} años, MTTR {MTTR_HOURS:g} h, '
              f'semilla {seed} en todas las variantes (números aleatorios comunes; la última fila '
              f'reproduce la de out/rail-e4). Umbral ≥ {a.target:g} %; con margen desde '
              f'{100 - 0.9 * (100 - a.target):.4f} %.', '',
              '| Estructura | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |',
              '|---|---|---|---|---|---|']
    for label, factors in variants:
        mean, low, high, exact, res = _mc(factors, seed, a.target)
        inside = 'sí' if low <= exact <= high else 'no'
        lines.append(f'| {label} | {mean:.4f} % | [{low:.4f}; {high:.4f}] | {exact:.4f} % | '
                     f'{inside} | {res} |')
    lines.append('')
    return a, full


def _crossing(full, level):
    """beta at which the Lab 3 formula equals level (bisection; the formula falls with beta)."""
    def f(b):
        return analytic_availability([(av, n, b if n > 1 else bb) for av, n, bb in full])
    lo, hi = 0.0, 1.0
    if f(lo) < level:
        return None
    for _ in range(60):
        mid = (lo + hi) / 2
        if f(mid) >= level:
            lo = mid
        else:
            hi = mid
    return lo


def sensitivity_beta(a, full, lines):
    lines += ['## 3. Sensibilidad de P7 a β (rail-e4, todos los grupos con el mismo β)', '',
              '| β | Semilla | Estimación | IC 95 % | Conocido (Lab 3) | ¿Dentro? | Resultado |',
              '|---|---|---|---|---|---|---|']
    for i, beta in enumerate(BETAS):
        factors = [(av, n, beta if n > 1 else b) for av, n, b in full]
        seed = 1200 + i
        mean, low, high, exact, res = _mc(factors, seed, a.target)
        inside = 'sí' if low <= exact <= high else 'no'
        lines.append(f'| {beta:.2f} | {seed} | {mean:.4f} % | [{low:.4f}; {high:.4f}] | '
                     f'{exact:.4f} % | {inside} | {res} |')
    b_threshold = _crossing(full, a.target)
    b_margin = _crossing(full, a.target + availability_margin(a.target))
    lines += ['', f'Según la fórmula del Lab 3, P7 cumple el umbral ({a.target:g} %) mientras '
              f'β ≤ {b_threshold:.3f} y lo cumple con margen ({a.target + availability_margin(a.target):.3f} %) '
              f'mientras β ≤ {b_margin:.3f}. El MC clasifica por el extremo bajo del IC, que es más '
              'exigente que el valor puntual.', '']


def main():
    mm = create_metamodel()
    lines = ['# Tácticas de las iteraciones 2 y 4 (equipo F)', '']
    contribution_p1(mm, lines)
    if os.path.exists('models/rail-e4.arch'):
        a, full = contribution_t41(mm, lines)
        sensitivity_beta(a, full, lines)
    os.makedirs('out/tactics', exist_ok=True)
    with open('out/tactics/tactics.md', 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
