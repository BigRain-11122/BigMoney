lines = open('scripts/trial_labor_w17.py', encoding='utf-8').read().splitlines()
for n, l in enumerate(lines, 1):
    if '"grammar"' in l or 'GRAMMAR = json.load' in l:
        print(n, ':', l)
