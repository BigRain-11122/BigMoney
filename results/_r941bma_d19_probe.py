# r941 D-19 decision/orders watermark check (python raw-bytes canonical; r828/r832/r814 laws)
import subprocess, hashlib, json, io

GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
GIT = r'C:\Program Files\Git\cmd\git.exe'

def git(*a, cwd=GRP):
    r = subprocess.run([GIT] + list(a), capture_output=True, cwd=cwd)
    return r.returncode, r.stdout, r.stderr

rc, _, err = git('fetch', 'origin')
print('group fetch rc=', rc, err.decode('utf-8','replace')[:120].strip())

out = {}
for doc, key in [('docs/decisions.md', 'decisions'), ('docs/orders.md', 'orders')]:
    rc, raw, err = git('show', 'origin/main:' + doc)
    if rc != 0:
        out[key] = {'rc': rc, 'error': err.decode('utf-8', 'replace')[:200]}
        continue
    h = hashlib.sha256(raw).hexdigest()
    out[key] = {'rc': 0, 'sha256': h, 'bytes': len(raw)}
    print(doc, 'sha256:', h, 'bytes:', len(raw))

state = json.load(io.open('state-bm-a.json', encoding='utf-8'))
prev_dec = state.get('last_decisions_sha', '')
prev_ord = state.get('last_orders_sha', '')
print('prev decisions sha:', prev_dec)
print('prev orders sha:', prev_ord)
print('DEC MATCH:', out['decisions'].get('sha256') == prev_dec)
print('ORD MATCH:', out['orders'].get('sha256') == prev_ord)
io.open('results/_r941bma_d19_probe.json', 'w', encoding='utf-8', newline='').write(
    json.dumps({'round': 'r941', 'probe': out, 'prev_decisions_sha': prev_dec, 'prev_orders_sha': prev_ord}, indent=1))
