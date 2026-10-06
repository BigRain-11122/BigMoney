# -*- coding: utf-8 -*-
# r788 bm-a: structure probe of runnable_pool.bm-a.json stages (schema discovery)
import subprocess, json

P = 'results/runnable_pool.bm-a.json'
def blob(spec):
    b = subprocess.run(['git', 'show', spec], capture_output=True).stdout
    return json.loads(b)

ours = blob(':2:' + P)
theirs = blob(':3:' + P)
for name, d in (('ours', ours), ('theirs', theirs)):
    print(name, 'top keys=', list(d.keys()))
    for k, v in d.items():
        if isinstance(v, list):
            print('  ', k, 'list len=', len(v), 'first keys=', list(v[0].keys())[:10] if v and isinstance(v[0], dict) else type(v[0]).__name__ if v else 'empty')
        elif isinstance(v, dict):
            print('  ', k, 'dict len=', len(v))
        else:
            print('  ', k, '=', str(v)[:80])
# locate owner_since anywhere
def find_os(d, path=''):
    hits = []
    if isinstance(d, dict):
        for k, v in d.items():
            p = path + '/' + str(k)
            if k in ('owner_since', 'owner', 'entry', 'status', 'cleared_ts'):
                hits.append((p, v))
            hits += find_os(v, p)
    elif isinstance(d, list):
        for i, v in enumerate(d[:400]):
            hits += find_os(v, path + '/%d' % i)
    return hits

for name, d in (('ours', ours), ('theirs', theirs)):
    hits = [h for h in find_os(d) if 'owner_since' in h[0]]
    print(name, 'owner_since hits=', len(hits))
    for p, v in hits[:12]:
        print('   ', p, '=', v)
