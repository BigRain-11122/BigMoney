import json, subprocess, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Tools'))
from fill_ladder import _write_pool_double

def show(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    return json.loads(r.stdout.decode('utf-8'))

head = show('HEAD:results/runnable_pool.json')      # upstream (bm-c tick, carries their 06:50:05 claim)
mine = show('REBASE_HEAD:results/runnable_pool.json')  # my r449 flip (burn complete + done)

# union: take upstream pool as base (131 identical entries verified), overlay my
# SLOT-6 done-flip; preserve bm-c claim fact as an honest collision note in the
# shard (r255 stale-tree claim family: their claim 06:50:05 post-dates my burn
# complete 06:40:34; commit-time ordering = bm-b adoption lands first).
hm = {e.get('id'): e for e in head['entries']}
mm = {e.get('id'): e for e in mine['entries']}
assert set(hm) == set(mm) and len(hm) == 132

mine6 = mm['INNOVATION-QUOTA-SLOT-6']
head6 = hm['INNOVATION-QUOTA-SLOT-6']
assert mine6['status'] == 'done' and head6['status'] == 'ready'
assert head6['shards'][0]['owner'] == 'bm-c' and head6['shards'][0]['owner_since'] == '2026-09-30 06:50:05'

shard = dict(mine6['shards'][0])
shard['note'] = (shard['note'] +
                 "; claim-collision honest note r449 bm-b: bm-c tick claim 06:50:05 post-dates "
                 "bm-b burn-complete 06:40:34 (r255 stale-tree family, verdict unpushed in window); "
                 "bm-c duplicate-burn if any = same-seed deterministic face, their side self-resolves per r450/r446 law")
union6 = dict(mine6)
union6['shards'] = [shard]

pool = dict(head)
for i, e in enumerate(pool['entries']):
    if e.get('id') == 'INNOVATION-QUOTA-SLOT-6':
        pool['entries'][i] = union6

# every other entry identical check
for e in pool['entries']:
    if e.get('id') != 'INNOVATION-QUOTA-SLOT-6':
        assert e == hm[e.get('id')] == mm[e.get('id')], e.get('id')

root = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
shared = os.path.join(root, 'results', 'runnable_pool.json')
lane = os.path.join(root, 'results', 'runnable_pool.bm-b.json')
_write_pool_double(shared, lane, pool)

b1 = open(shared, 'rb').read(); b2 = open(lane, 'rb').read()
assert b1 == b2
d = json.loads(b1.decode('utf-8'))
ent = [e for e in d['entries'] if e.get('id') == 'INNOVATION-QUOTA-SLOT-6'][0]
assert ent['status'] == 'done' and ent['shards'][0]['status'] == 'done'
assert 'claim-collision honest note' in ent['shards'][0]['note']
print('UNION LANDED: SLOT-6 done (bm-b burn) + bm-c 06:50:05 claim-collision note preserved; shared==lane byte-identical')
