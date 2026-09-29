import re
src = open('scripts/trial_labor_w10.py', encoding='utf-8').read().split('\n')
pat = re.compile(r'mom|_w10\(|w10_|"mom"|axis_config')
hits = []
for i, l in enumerate(src):
    if pat.search(l):
        hits.append(i + 1)
ranges = []
prev = None
start = None
for h in hits:
    if prev is None or h - prev > 2:
        if start:
            ranges.append((start, prev))
        start = h
    prev = h
if start:
    ranges.append((start, prev))
print('mom-touching line ranges:')
for r in ranges:
    print(' ', r)
print('total hit lines', len(hits), 'of', len(src))
