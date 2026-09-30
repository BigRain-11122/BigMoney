import re
live = open('scripts/trial_labor_w12.py', encoding='utf-8').read()
lines = live.splitlines()
idx = [i for i, l in enumerate(lines) if re.search(r'\bpf\b\s*=', l) or 'json.load(open' in l and 'probe' in l.lower()]
for i in idx[:12]:
    print('%5d: %s' % (i+1, lines[i].strip()[:120]))
print()
# context around pf usage in L7 region
i = [j for j, l in enumerate(lines) if 'L7g' in l]
if i:
    for j in range(i[0]-14, i[0]+6):
        print('%5d: %s' % (j+1, lines[j]))
