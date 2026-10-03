import json, glob
sh = json.load(open('results/compute_audit.json', encoding='utf-8'))
lanes = {}
for f in glob.glob('results/compute_audit.bm-*.json'):
    mid = f.split('.')[-2]
    lanes[mid] = json.load(open(f, encoding='utf-8'))
sh_h = {r['ts']: r for r in sh.get('history', [])}
print('shared rows:', len(sh_h))
union_keys = set()
per = {}
for mid, lv in lanes.items():
    ks = {r['ts'] for r in lv.get('history', [])}
    per[mid] = len(ks)
    union_keys |= ks
print('lane files:', per, 'union rows:', len(union_keys))
missing_from_shared = union_keys - set(sh_h)
extra_in_shared = set(sh_h) - union_keys
print('union rows MISSING from shared:', sorted(missing_from_shared)[:8])
print('shared rows NOT in any lane-file (on this disk):', sorted(extra_in_shared)[:8])
# r85 window survival: producer window first ts boundary
wfirst = min(sh_h)
inwin = {k for k in union_keys if k >= wfirst}
print('window first ts:', wfirst, 'in-window union:', len(inwin), 'in-window missing:', len([k for k in inwin if k not in sh_h]))
