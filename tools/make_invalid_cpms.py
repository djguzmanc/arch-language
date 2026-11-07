"""[A] Writes the ill-formed models of team A (CPMS) in invalid/, one per constraint added
by the team (C8, C9, C10) plus the C4 case observed in the feedback of Delivery 1.
Each one is models/cpms-l1.arch with a single change. Run from the root of the repository:

    python tools/make_invalid_cpms.py
"""
src = open('models/cpms-l1.arch', encoding='utf-8').read()


def mutate(name, old, new):
    assert src.count(old) == 1, (name, src.count(old))
    with open(f'invalid/{name}.arch', 'w', encoding='utf-8', newline='\n') as f:
        f.write(src.replace(old, new))


# C4 (Laboratory 4 rule, store without domain): feedback of Delivery 1, T3.12 reads the
# berth store T4.2 directly instead of going through T3.1.
mutate('cpms-c4-store-shared',
       '// Planificación intermodal (interna)\n',
       '// Planificación intermodal (interna)\n'
       'connector A-K99 nature dependency coupling blocking\n'
       '    carries "Lectura directa de escalas y atraques, sin pasar por T3.1 (feedback E1)"'
       ' : T3.12 -> T4.2\n')

# C8 (gateway pattern): the road gateway reaches the gate logic T3.6 instead of CGW.
mutate('cpms-c8-boundary-not-at-gateway',
       'availability 99.95\n    : RGW -> CGW\nconnector SoS_K1b',
       'availability 99.95\n    : RGW -> T3.6\nconnector SoS_K1b')

# C9 (hierarchical style and control loop): T3.10 commands the quay crane directly,
# bypassing its on-board computer T5.8.
mutate('cpms-c9-equipment-with-two-authorities',
       '// Datos de campo hacia el sistema\n',
       '// Datos de campo hacia el sistema\n'
       'connector A-K99 nature control_command coupling supply\n'
       '    carries "Orden directa a la grúa de muelle, saltando el lazo de control"'
       ' : T3.10 -> T5.1\n')

# C10 (event-based style): the broker waits for the gate logic before going on.
mutate('cpms-c10-event-with-blocking-coupling',
       'connector A-K22 nature event_notification coupling supply',
       'connector A-K22 nature event_notification coupling blocking')
