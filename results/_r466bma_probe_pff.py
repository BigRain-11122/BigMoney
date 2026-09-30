import re
for name, path in (('DRAFT', 'results/_r464bma_w13_runner_draft.py'),
                   ('LIVE', 'scripts/trial_labor_w12.py')):
    src = open(path, encoding='utf-8').read()
    i = src.find('PROBE_FACTS_FILE =')
    print(name, repr(src[i:i+220]))
    print()
