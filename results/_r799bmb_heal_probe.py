import subprocess, json, hashlib

def show(ref, path):
    r = subprocess.run(['git', 'show', ref + ':' + path], capture_output=True)
    return r.stdout

def jd(b):
    return json.loads(b.decode('utf-8'))

def sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:16]

# theirs base = b25a0cb91 (bm-a r811 churn-absorb-7, the rebase base r798 replayed onto)
REFS = {'ours_pre': '7ffcd2011', 'theirs_base': 'b25a0cb91'}

for tag, path in [('compute_audit', 'results/compute_audit.json'),
                  ('regime_state', 'results/regime_state.json')]:
    faces = {}
    for name, ref in REFS.items():
        try:
            faces[name] = jd(show(ref, path))
        except Exception as e:
            faces[name] = None
            print(tag, name, 'LOAD-ERR', str(e)[:100])
    cur = jd(open(path, 'rb').read())
    faces['current'] = cur
    if any(v is None for v in faces.values()):
        continue
    print('==', tag)
    for k in ('history', 'runs'):
        if k in cur and isinstance(cur[k], list) and all(isinstance(f.get(k), list) for f in faces.values()):
            rows = {n: {sha(r): r for r in f[k]} for n, f in faces.items()}
            print('  ', k, 'counts:', {n: len(v) for n, v in rows.items()})
            for a, b in [('ours_pre', 'theirs_base'), ('theirs_base', 'current'), ('ours_pre', 'current')]:
                lost = set(rows[b]) - set(rows[a])
                print(f'   {a} -> {b}: +{len(lost)}', [rows[b][i] for i in sorted(lost)][:2])
    for k in set(cur) - {'history', 'runs'}:
        vals = {n: sha(f.get(k)) for n, f in faces.items() if f is not None}
        if len(set(vals.values())) > 1:
            print('  ', k, vals)
