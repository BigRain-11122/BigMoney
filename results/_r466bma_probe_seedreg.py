import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
i = draft.find('SEED_REGISTRY')
print(repr(draft[i:i+700]))
print()
for pat in ['trial_labor_w13_gen', 'trial_labor_w13_unc', 'trial_labor_w13_scrnull']:
    print(pat, '->', draft.count(pat))
# tl12. references with _w12 suffix (overreach-guard scope)
for m in re.finditer(r'tl12\.[A-Za-z_][A-Za-z0-9_]*_w12\b', draft):
    print('OVERREACH-RISK:', m.group(0))
