# r806 bm-b D-19 dual read (r804 recipe verbatim lineage: ssh-first dual-URL, unique temp dir,
# --no-checkout zero tree touch, byte-precise sha256; watermarks read dynamically from state.json)
import hashlib, json, os, shutil, subprocess

REPOS = ['git@github.com:BigRain-11122/FluxGroup.git',
         'https://github.com/BigRain-11122/FluxGroup.git']

s = json.load(open('state.json', encoding='utf-8'))
W_DECISIONS = s.get('last_decisions_sha', '')
W_ORDERS = s.get('last_orders_sha', '')

tmp = os.path.join(os.environ['TEMP'], 'd19_r806')
if os.path.isdir(os.path.join(tmp, '.git')):
    r = subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
if not os.path.isdir(os.path.join(tmp, '.git')):
    got = None
    for r0 in REPOS:
        k = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout', r0, tmp],
                           capture_output=True, text=True)
        if k.returncode == 0:
            got = r0
            break
    assert got, 'all clone URLs failed'

st = {'round': 'r806', 'w_decisions': W_DECISIONS[:8], 'w_orders': str(W_ORDERS)[:8]}
def blob(path):
    r = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:' + path], capture_output=True)
    assert r.returncode == 0, path + ' unavailable: ' + r.stderr.decode('utf-8', 'replace')[:200]
    return r.stdout

dec = blob('docs/decisions.md')
ordr = blob('docs/orders.md')
st['decisions_sha256'] = hashlib.sha256(dec).hexdigest().upper()
st['orders_sha256'] = hashlib.sha256(ordr).hexdigest().upper()
st['decisions_changed'] = st['decisions_sha256'] != W_DECISIONS
st['orders_changed'] = st['orders_sha256'] != W_ORDERS
st['decisions_bytes'] = len(dec)
st['orders_bytes'] = len(ordr)

dec_txt = dec.decode('utf-8', 'replace')
ord_txt = ordr.decode('utf-8', 'replace')
if st['decisions_changed']:
    st['decisions_tail40'] = dec_txt.splitlines()[-40:]
if st['orders_changed']:
    hits = [l for l in ord_txt.splitlines() if ('BigMoney' in l or 'bigmoney' in l or 'bm-b' in l)]
    st['orders_bmb_rows'] = hits[-30:]
    st['orders_tail25'] = ord_txt.splitlines()[-25:]

json.dump(st, open('results/_r806bmb_d19_read.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps({k: st[k] for k in ['w_decisions', 'w_orders', 'decisions_sha256', 'orders_sha256',
      'decisions_changed', 'orders_changed', 'decisions_bytes', 'orders_bytes']}, ensure_ascii=False))
