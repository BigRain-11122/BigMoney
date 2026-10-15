import hashlib, subprocess, json, re

G = r'C:/Users/sjs20/Desktop/FluxGroup'
out = {}
for key, path in (('dec', 'docs/decisions.md'), ('ord', 'docs/orders.md')):
    r = subprocess.run(['git', '-C', G, 'show', 'origin/main:' + path], capture_output=True, timeout=60)
    out[key] = hashlib.sha256(r.stdout).hexdigest()

st = open('state-bm-a.json', encoding='utf-8').read()
dec_prev = re.search(r'"last_decisions_sha":\s*"([0-9a-f]{64})"', st).group(1)
ord_prev = re.search(r'"last_orders_sha":\s*"([0-9a-f]{64})"', st).group(1)
print('DEC', out['dec'][:16], 'MATCH' if out['dec'] == dec_prev else 'DELTA from ' + dec_prev[:16])
print('ORD', out['ord'][:16], 'MATCH' if out['ord'] == ord_prev else 'DELTA from ' + ord_prev[:16])
print('NEW_DEC_FULL', out['dec'])
print('NEW_ORD_FULL', out['ord'])
