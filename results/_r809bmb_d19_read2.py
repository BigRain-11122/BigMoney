# r809 bm-b D-19 FRESH dual read (C7 heal face): local group tree first, temp sparse clone
# fallback; sha256 (legacy continuity face) + sha1 40-hex (ALGORITHM PIN r537 fleet face).
import hashlib, json, os, shutil, subprocess

REPOS = ['git@github.com:BigRain-11122/FluxGroup.git',
         'https://github.com/BigRain-11122/FluxGroup.git']
LOCAL_GROUP = r'C:\Fluxgroup\FluxGroup'

s = json.load(open('state.json', encoding='utf-8'))
W_DEC = s.get('last_decisions_sha', '')
W_ORD = s.get('last_orders_sha', '')

st = {'round': 'r809', 'mode': '', 'w_decisions': str(W_DEC)[:8], 'w_orders': str(W_ORD)[:8]}
dec = ordr = None

def try_local():
    global dec, ordr
    if not os.path.isdir(os.path.join(LOCAL_GROUP, '.git')):
        return False
    r = subprocess.run(['git', '-C', LOCAL_GROUP, 'fetch', 'origin'],
                       capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        st['local_fetch_err'] = r.stderr.strip()[-200:]
        return False
    st['mode'] = 'local group tree fetch+show'
    for key, path in (('dec', 'docs/decisions.md'), ('ord', 'docs/orders.md')):
        g = subprocess.run(['git', '-C', LOCAL_GROUP, 'show', 'origin/main:' + path],
                           capture_output=True)
        if g.returncode != 0:
            return False
        if key == 'dec':
            dec = g.stdout
        else:
            ordr = g.stdout
    h = subprocess.run(['git', '-C', LOCAL_GROUP, 'rev-parse', 'origin/main'],
                      capture_output=True, text=True)
    st['origin_main'] = h.stdout.strip()
    return True

def try_clone():
    global dec, ordr
    tmp = os.path.join(os.environ['TEMP'], 'd19_r809')
    if os.path.isdir(os.path.join(tmp, '.git')):
        r = subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True, timeout=120)
        if r.returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
    if not os.path.isdir(os.path.join(tmp, '.git')):
        got = None
        for r0 in REPOS:
            k = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none',
                                '--no-checkout', r0, tmp], capture_output=True, text=True, timeout=120)
            if k.returncode == 0:
                got = r0
                break
        if not got:
            return False
    st['mode'] = 'temp sparse clone (r631 recipe)'
    for key, path in (('dec', 'docs/decisions.md'), ('ord', 'docs/orders.md')):
        g = subprocess.run(['git', '-C', tmp, 'show', 'origin/main:' + path], capture_output=True)
        if g.returncode != 0:
            return False
        if key == 'dec':
            dec = g.stdout
        else:
            ordr = g.stdout
    h = subprocess.run(['git', '-C', tmp, 'rev-parse', 'origin/main'], capture_output=True, text=True)
    st['origin_main'] = h.stdout.strip()
    return True

ok = try_local() or try_clone()
st['read_ok'] = ok
if ok:
    st['decisions_sha256'] = hashlib.sha256(dec).hexdigest().upper()
    st['orders_sha256'] = hashlib.sha256(ordr).hexdigest().upper()
    st['decisions_sha1'] = hashlib.sha1(dec).hexdigest().upper()
    st['orders_sha1'] = hashlib.sha1(ordr).hexdigest().upper()
    st['fleet_dec_pin'] = 'BD94A27BA4AC39BC'  # bm-c MSG C7 fleet current face 10-09 16:50
    st['dec_joins_fleet_pin'] = st['decisions_sha1'].startswith('BD94A27B')
    # change detection: compare vs stored (legacy sha256 base) AND report both faces
    st['decisions_changed_vs_local_wm'] = st['decisions_sha256'] != W_DEC
    st['orders_changed_vs_local_wm'] = st['orders_sha256'] != W_ORD
    st['decisions_bytes'] = len(dec)
    st['orders_bytes'] = len(ordr)
    dec_txt = dec.decode('utf-8', 'replace')
    ord_txt = ordr.decode('utf-8', 'replace')
    if st['decisions_changed_vs_local_wm']:
        st['decisions_tail60'] = dec_txt.splitlines()[-60:]
    hits = [l for l in ord_txt.splitlines()
            if ('BigMoney' in l or 'bigmoney' in l or 'bm-b' in l)]
    st['orders_bmb_rows'] = hits[-30:]
else:
    st['error'] = 'both local and clone reads failed'

json.dump(st, open('results/_r809bmb_d19_read2.json', 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
keep = ['read_ok', 'mode', 'origin_main', 'decisions_sha256', 'orders_sha256',
        'decisions_sha1', 'orders_sha1', 'dec_joins_fleet_pin',
        'decisions_changed_vs_local_wm', 'orders_changed_vs_local_wm',
        'decisions_bytes', 'orders_bytes']
print(json.dumps({k: st.get(k) for k in keep}, ensure_ascii=False))
