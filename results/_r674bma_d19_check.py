# r674 bm-a D-19 decisions watermark check (subprocess raw bytes per r660 law; sparse-clone fallback per D-20261004-02③)
import json, subprocess, hashlib, sys, os, tempfile, shutil

def sha256(b): return hashlib.sha256(b).hexdigest()

out = {'tree_used': None, 'mode': None}

cands = []
for p in (r'K:\Fluxgroup\FluxGroup', r'C:\Fluxgroup\FluxGroup'):
    if os.path.exists(p): cands.append(p)

tree = cands[0] if cands else None
db = ob = None
if tree:
    subprocess.run(['git', '-C', tree, 'fetch', 'origin'], capture_output=True)
    def show_bytes(t, path):
        r = subprocess.run(['git', '-C', t, 'show', 'origin/main:' + path], capture_output=True)
        return r.stdout if r.returncode == 0 else None
    db = show_bytes(tree, 'docs/decisions.md'); ob = show_bytes(tree, 'docs/orders.md')
    out['mode'] = 'local-tree'
    out['tree_used'] = tree

if db is None:
    # sparse clone fallback (r631 bm-b recipe: depth1 blobless sparse, read origin blob, zero persistent tree)
    tmp = os.path.join(tempfile.gettempdir(), '_r674bma_fluxgroup_sparse')
    if os.path.exists(tmp): shutil.rmtree(tmp, ignore_errors=True)
    r = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--sparse',
                         'https://github.com/BigRain-11122/FluxGroup.git', tmp], capture_output=True)
    if r.returncode != 0:
        out['mode'] = 'sparse-clone-FAIL'; out['err'] = r.stderr.decode('utf-8', 'replace')[:400]
    else:
        subprocess.run(['git', '-C', tmp, 'sparse-checkout', 'set', '--skip-checks', 'docs/decisions.md', 'docs/orders.md'], capture_output=True)
        subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True)
        def show2(path):
            rr = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:' + path], capture_output=True)
            return rr.stdout if rr.returncode == 0 else None
        db = show2('docs/decisions.md'); ob = show2('docs/orders.md')
        out['mode'] = 'sparse-clone'
    shutil.rmtree(tmp, ignore_errors=True)

if db is not None:
    out['decisions_sha256'] = sha256(db); out['decisions_len'] = len(db)
if ob is not None:
    out['orders_sha256'] = sha256(ob); out['orders_len'] = len(ob)
    txt = ob.decode('utf-8', 'replace')
    out['orders_bigmoney_lines'] = [l for l in txt.splitlines() if ('bigmoney' in l.lower() or 'quant' in l.lower())][-12:]

st = json.load(open('state-bm-a.json', 'rb'))
out['state_last_decisions_sha'] = st.get('last_decisions_sha')
out['match'] = (out.get('decisions_sha256') == st.get('last_decisions_sha'))
open('results/_r674bma_d19_check.json', 'wb').write(json.dumps(out, ensure_ascii=False, indent=1).encode('utf-8'))
print(json.dumps(out, ensure_ascii=False)[:3000])
