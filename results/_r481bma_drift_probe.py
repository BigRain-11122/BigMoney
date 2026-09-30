import json, io, os

# compute_audit: shared history vs lane-merged history (union of per-lane files)
shared = json.load(io.open('results/compute_audit.json', encoding='utf-8'))
sh_keys = set()
for h in shared.get('history', []):
    sh_keys.add(h.get('ts'))

lane_keys = set()
for lane in ('bm-a', 'bm-b', 'bm-c'):
    p = f'results/compute_audit.{lane}.json'
    if os.path.exists(p):
        d = json.load(io.open(p, encoding='utf-8'))
        for h in d.get('history', []):
            lane_keys.add(h.get('ts'))

only_shared = sorted(sh_keys - lane_keys)
only_lane = sorted(lane_keys - sh_keys)
print('compute_audit: shared rows', len(sh_keys), '| lane-union rows', len(lane_keys))
print('  shared-only ts count:', len(only_shared), 'sample:', only_shared[:5])
print('  lane-only ts count:', len(only_lane), 'sample:', only_lane[:5])

# gate_attrition: shared vs lane files entries
shared_ga = json.load(io.open('results/gate_attrition.json', encoding='utf-8'))
se = shared_ga.get('entries', [])
se_keys = set()
for e in se:
    k = (e.get('batch'), e.get('family') if 'family' in e else None)
    se_keys.add(e.get('batch'))
lane_keys_ga = set()
for lane in ('bm-a', 'bm-b', 'bm-c'):
    p = f'results/gate_attrition.{lane}.json'
    if os.path.exists(p):
        d = json.load(io.open(p, encoding='utf-8'))
        for e in d.get('entries', []):
            lane_keys_ga.add(e.get('batch'))
print('gate_attrition: shared batches', len(se_keys), '| lane-union batches', len(lane_keys_ga))
print('  shared-only:', sorted(se_keys - lane_keys_ga)[:8])
print('  lane-only:', sorted(lane_keys_ga - se_keys)[:8])
print('  shared entries len', len(se))
