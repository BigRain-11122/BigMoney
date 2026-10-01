import sys, json
p = r'results/pool_core_samples.jsonl'
raw = open(p, 'rb').read().decode('utf-8')
lines = raw.split('\n')
# locate conflict region
i0 = next(i for i,l in enumerate(lines) if l.startswith('<<<<<<<'))
im = next(i for i,l in enumerate(lines) if l.startswith('=======') and i > i0)
i1 = next(i for i,l in enumerate(lines) if l.startswith('>>>>>>>') and i > im)
head_side = [l for l in lines[i0+1:im] if l.strip()]
ours_side = [l for l in lines[im+1:i1] if l.strip()]
# union by full-line identity (telemetry rows unique per ts+pid+machine)
seen = set(); merged = []
for l in head_side + ours_side:
    if l not in seen:
        seen.add(l); merged.append(l)
merged.sort(key=lambda l: json.loads(l).get('ts',''))
out = lines[:i0] + merged + lines[i1+1:]
open(p, 'wb').write('\n'.join(out).encode('utf-8'))
print('union rows: head=%d ours=%d merged=%d' % (len(head_side), len(ours_side), len(merged)))
# sanity: whole file parse
for l in open(p, encoding='utf-8'):
    if l.strip(): json.loads(l)
print('all lines parse OK')
