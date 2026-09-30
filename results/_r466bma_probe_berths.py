draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
lines = draft.splitlines()
for i, l in enumerate(lines):
    if '20321500' in l or ('20321000' in l and 'berth' in l) or '20323500' in l:
        print('%5d: %s' % (i+1, l.strip()[:125]))
# full dual-nulls docstring region
i = [j for j, l in enumerate(lines) if 'def _dual_nulls_w12' in l]
if i:
    print('--- dual nulls def region ---')
    for j in range(i[0], min(i[0]+22, len(lines))):
        print('%5d: %s' % (j+1, lines[j]))
