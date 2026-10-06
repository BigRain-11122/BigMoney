# -*- coding: utf-8 -*-
# r788 bm-a: locate contested fund-* entries in both stages of runnable_pool.bm-a.json
import subprocess, json

P = 'results/runnable_pool.bm-a.json'
def blob(spec):
    return json.loads(subprocess.run(['git', 'show', spec], capture_output=True).stdout)

ours = blob(':2:' + P); theirs = blob(':3:' + P)

def idx(d):
    m = {}
    for e in d['entries']:
        for sh in e.get('shards', []):
            m[sh.get('shard_id') or (e['id'] + '|' + str(sh.get('shard')))] = (e, sh)
    return m

io, it = idx(ours), idx(theirs)
print('ours shard index=', len(io), 'theirs=', len(it))
only_o = set(io) - set(it); only_t = set(it) - set(io)
print('only-in-ours=', sorted(only_o)[:8]); print('only-in-theirs=', sorted(only_t)[:8])

diffs = []
for k in set(io) & set(it):
    a, b = io[k][1], it[k][1]
    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
        diffs.append(k)
print('differing shards=', len(diffs))
for k in sorted(diffs):
    a, b = io[k][1], it[k][1]
    print('---', k)
    for f in sorted(set(a) | set(b)):
        if a.get(f) != b.get(f):
            print('   ours', f, '=', a.get(f))
            print('   their', f, '=', b.get(f))
    # entry-level diff too
    ea, eb = io[k][0], it[k][0]
    for f in sorted(set(ea) | set(eb)):
        if f == 'shards':
            continue
        if json.dumps(ea.get(f), sort_keys=True) != json.dumps(eb.get(f), sort_keys=True) and f in ('status', 'done_at', 'cleared_ts', 'note'):
            print('   [entry] ours', f, '=', str(ea.get(f))[:100])
            print('   [entry] their', f, '=', str(eb.get(f))[:100])
