import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
lines = draft.splitlines()
# loader disc keys
i = draft.find('def _load_exclusion_rows_w13')
print('loader fn at char', i, 'found' if i >= 0 else 'NOT FOUND')
if i >= 0:
    seg = draft[i:i+4600]
    for ln in seg.splitlines():
        if 'disc[' in ln and 'survivors' in ln or 'judge_products' in ln:
            print('KEY:', ln.strip()[:120])
print()
# L9a region
idx = [j for j, l in enumerate(lines) if 'L9a exclusion loader' in l]
print('L9a at line', idx)
if idx:
    for j in range(idx[0], idx[0] + 15):
        print('%5d: %s' % (j+1, lines[j]))
print()
# disc set usages of w12/w13 names
for j, l in enumerate(lines):
    if 'w12_screen_survivors' in l or 'w13_screen_survivors' in l:
        print('%5d: %s' % (j+1, l.strip()[:120]))
