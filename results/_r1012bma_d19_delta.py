"""r1012 bm-a D-19 dual-delta: fetch group tree (C: real-path), read orders.md +
decisions.md from origin/main blobs raw-bytes, sha256 vs state-bm-a.json watermarks.
Print delta tail rows for consumption decision. Read-only (watermark advance done
by closeout script)."""
import subprocess, json, hashlib, sys

GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
r = subprocess.run(['git', '-C', GRP, 'fetch', 'origin'], capture_output=True)
if r.returncode != 0:
    print('FETCH-FAIL', r.stderr.decode('utf-8', 'replace')[:200]); sys.exit(2)

def blob(path):
    return subprocess.check_output(['git', '-C', GRP, 'show', 'origin/main:%s' % path])

st = json.load(open('state-bm-a.json', encoding='utf-8-sig'))
out = {}
for key, path in (('orders', 'docs/orders.md'), ('decisions', 'docs/decisions.md')):
    b = blob(path)
    h = hashlib.sha256(b).hexdigest()
    prev = st.get('last_%s_sha' % key)
    out[key] = {'sha': h, 'prev': prev, 'changed': h != prev, 'bytes': len(b)}
    if h != prev:
        lines = [l for l in b.decode('utf-8', 'replace').splitlines() if l.strip()]
        out[key]['total_lines'] = len(lines)
        out[key]['tail'] = lines[-40:]
print(json.dumps({'orders': {k: v for k, v in out['orders'].items() if k != 'tail'},
                 'decisions': {k: v for k, v in out['decisions'].items() if k != 'tail'}}, indent=1))
for key in ('orders', 'decisions'):
    if out[key].get('tail'):
        print('=== %s TAIL ===' % key.upper())
        print('\n'.join(out[key]['tail']))
