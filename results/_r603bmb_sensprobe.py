import json, subprocess

def pool_from(ref):
    if ref == 'WORKTREE':
        with open('results/runnable_pool.json', 'rb') as f:
            return json.loads(f.read().decode('utf-8'))
    out = subprocess.run(['git', 'show', ref + ':results/runnable_pool.json'],
                         capture_output=True).stdout
    return json.loads(out.decode('utf-8'))

for label, ref in (('ORIGIN', 'origin/main'), ('LOCAL', 'WORKTREE'),
                   ('MERGEBASE', '0210dfff6')):
    d = pool_from(ref)
    entries = d.get('entries') if isinstance(d, dict) else d
    if isinstance(entries, dict):
        entries = list(entries.values())
    print('==', label, '==')
    for e in entries:
        if 'sens' in json.dumps(e):
            keys = ('id', 'status', 'owner', 'claimed_by', 'claimed_at',
                    'updated_at', 'result_ref', 'shards')
            print(json.dumps({k: e.get(k) for k in keys}, ensure_ascii=False)[:600])
