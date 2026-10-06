# -*- coding: utf-8 -*-
# r788 bm-a: probe both merge stages of runnable_pool.bm-a.json (R31 lane authority law --
# owner machine side wins for lane files; claw said origin carries owner_since 18:18:09 newer).
import subprocess, json

P = 'results/runnable_pool.bm-a.json'
def blob(spec):
    b = subprocess.run(['git', 'show', spec], capture_output=True).stdout
    return json.loads(b)

ours = blob(':2:' + P)    # merge window: stage2 = ours = HEAD (local bm-a)
theirs = blob(':3:' + P)  # stage3 = theirs = MERGE_HEAD (origin)

def entries(d):
    pool = d.get('pool', d if isinstance(d, dict) else {})
    if isinstance(pool, list):
        return {e.get('entry'): e for e in pool}
    return {k: v for k, v in pool.items() if isinstance(v, dict)}

eo, et = entries(ours), entries(theirs)
print('ours entries=', len(eo), 'theirs entries=', len(et))
probes = ['fund-quality-p1-nulls-0of1', 'fund-divlowvol-p1-nulls-0of1', 'fund-value-p1-nulls-0of1']
for k in probes:
    o, t = eo.get(k), et.get(k)
    print(k)
    print('  ours  owner_since=', (o or {}).get('owner_since'), 'owner=', (o or {}).get('owner'))
    print('  their owner_since=', (t or {}).get('owner_since'), 'owner=', (t or {}).get('owner'))
# key set diff
only_o = set(eo) - set(et); only_t = set(et) - set(eo)
print('only-in-ours=', sorted(only_o)[:5]); print('only-in-theirs=', sorted(only_t)[:5])
# other differing entries
diff = [k for k in set(eo) & set(et) if json.dumps(eo[k], sort_keys=True) != json.dumps(et[k], sort_keys=True)]
print('differing common entries=', len(diff), diff[:8])
