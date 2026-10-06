import json, glob, os, sys
out = []
for p in sorted(glob.glob(r'fleet\tasks\*.json')):
    try:
        d = json.load(open(p, encoding='utf-8'))
    except Exception as e:
        out.append((p, 'PARSE_ERR', str(e)[:60], ''))
        continue
    out.append((os.path.basename(p), d.get('status', '?'), str(d.get('claimed_by', '')), str(d.get('title', d.get('subject', '')))[:90]))
open_stat = [r for r in out if r[1] == 'open']
claimed = [r for r in out if r[1] == 'claimed']
inprog = [r for r in out if r[1] == 'in_progress']
print('total tickets:', len(out), '| open:', len(open_stat), '| claimed:', len(claimed), '| in_progress:', len(inprog))
print('--- OPEN ---')
for r in open_stat: print(' ', r[0], '|', r[3])
print('--- CLAIMED/IN_PROGRESS (owners) ---')
for r in claimed + inprog: print(' ', r[0], '|', r[1], '| by', r[2], '|', r[3])
