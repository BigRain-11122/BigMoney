import hashlib, io, json, subprocess

GRP = r'K:\Fluxgroup\FluxGroup'
REPO = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

dec = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/decisions.md'], capture_output=True)
assert dec.returncode == 0, dec.stderr[:300]
dec_sha = hashlib.sha256(dec.stdout).hexdigest()

ordr = subprocess.run(['git', '-C', GRP, 'show', 'origin/main:docs/orders.md'], capture_output=True)
assert ordr.returncode == 0
ord_sha1 = hashlib.sha1(ordr.stdout).hexdigest()

st_path = REPO + r'\state-bm-c.json'
st = json.load(io.open(st_path, encoding='utf-8'))
prev_dec = st.get('last_decisions_sha')
prev_ord = st.get('last_orders_sha')
print('dec prev', prev_dec[:12] if prev_dec else None, 'now', dec_sha[:12], 'delta', prev_dec != dec_sha)
print('ord prev', prev_ord[:12] if prev_ord else None, 'now', ord_sha1[:12], 'delta', prev_ord != ord_sha1)

if dec_sha != prev_dec:
    text = dec.stdout.decode('utf-8', 'replace')
    hits = [ln for ln in text.splitlines() if ('BigMoney' in ln or 'bigmoney' in ln or 'quant' in ln)]
    print('dec-ish lines:', len(hits))
    for ln in hits[-6:]:
        print('  *', ln[:300])
if ord_sha1 != prev_ord:
    text = ordr.stdout.decode('utf-8', 'replace')
    hits = [ln for ln in text.splitlines() if ('BigMoney' in ln or 'bigmoney' in ln or 'quant' in ln)]
    print('ord-ish lines:', len(hits))
    for ln in hits[-6:]:
        print('  *', ln[:300])