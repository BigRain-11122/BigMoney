# r789 bm-b D-19 dual read (r770 bm-a recipe lineage: ssh-first dual-URL, unique temp dir,
# --no-checkout zero tree touch, byte-precise sha256; r677 SSL-transient law = ssh first)
import hashlib, json, os, shutil, subprocess

REPOS = ['git@github.com:BigRain-11122/FluxGroup.git',
         'https://github.com/BigRain-11122/FluxGroup.git']
W_DECISIONS = "A44C39E01F9781BE981E208A48D852F6BCEF44709D004128591A88DF13C62EFB"
W_ORDERS     = "9A273ECAEFDD9747002F2A0CA01099CCDBA6E96945C8BFE72A265C67650C99D3"

tmp = os.path.join(os.environ['TEMP'], 'd19_r789')
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

st = {'repo_used': tmp, 'repo_url': got if not os.path.isdir(os.path.join(tmp, '.git')) else 'cached-fetch'}
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

# dump dispatch-board block (派工通告板) + CEO pending rows for delta consumption if changed
dec_txt = dec.decode('utf-8', 'replace')
ord_txt = ordr.decode('utf-8', 'replace')
if st['decisions_changed']:
    lines = dec_txt.splitlines()
    st['decisions_tail40'] = lines[-40:]
if st['orders_changed']:
    hits = [l for l in ord_txt.splitlines() if ('BigMoney' in l or 'bigmoney' in l or 'bm-b' in l)]
    st['orders_bmb_rows'] = hits[-30:]
    st['orders_tail25'] = ord_txt.splitlines()[-25:]

with open('results/_r789bmb_d19_read.json', 'w', encoding='utf-8') as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print(json.dumps({k: st[k] for k in ('decisions_sha256', 'orders_sha256', 'decisions_changed', 'orders_changed')}, indent=1))
