# r770 bm-a D-19 fresh-read probe (r481/r677 recipe: ssh-first dual-URL, mkdtemp unique dir, byte-precise hash)
import hashlib, json, os, shutil, subprocess, tempfile

REPOS = ['git@github.com:BigRain-11122/FluxGroup.git',
         'https://github.com/BigRain-11122/FluxGroup.git']
tmp = os.path.join(os.environ['TEMP'], 'd19_r770')
if os.path.isdir(os.path.join(tmp, '.git')):
    r = subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
if not os.path.isdir(os.path.join(tmp, '.git')):
    got = None
    for r0 in REPOS:
        s = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', r0, tmp],
                           capture_output=True, text=True)
        if s.returncode == 0:
            got = r0
            break
    assert got, 'all clone URLs failed'
st = {}
out = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/decisions.md'], capture_output=True).stdout
st['decisions_sha256'] = hashlib.sha256(out).hexdigest()
st['decisions_bytes'] = len(out)
out2 = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:docs/orders.md'], capture_output=True).stdout
st['orders_sha256'] = hashlib.sha256(out2).hexdigest()
st['orders_bytes'] = len(out2)
with open(r'C:\Users\sjs20\AppData\Local\Temp\d19_r770_decisions.md', 'wb') as f:
    f.write(out)
with open(r'C:\Users\sjs20\AppData\Local\Temp\d19_r770_orders.md', 'wb') as f:
    f.write(out2)

prev = json.load(open('state-bm-a.json', encoding='utf-8-sig'))
st['prev_decisions_sha'] = prev.get('last_decisions_sha', '')
st['prev_orders_sha'] = prev.get('last_orders_sha', '')
st['decisions_match'] = st['decisions_sha256'].lower() == st['prev_decisions_sha'].lower()
st['orders_match'] = st['orders_sha256'].lower() == st['prev_orders_sha'].lower()
json.dump(st, open('results/_r770bma_d19_probe.json', 'w'), indent=1)
print(json.dumps({k: (v[:8] + '...' if isinstance(v, str) and len(v) > 12 else v) for k, v in st.items()}, indent=1))
