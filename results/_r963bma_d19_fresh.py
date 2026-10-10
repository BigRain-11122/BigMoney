# r963 fresh D-19/ORD delta read (C: real-path, raw bytes, UTF-8 out)
import subprocess, hashlib, io, json, os, time

GR = r'C:\Users\sjs20\Desktop\FluxGroup'
r = subprocess.run(['git', '-C', GR, 'fetch', 'origin'], capture_output=True, timeout=120)
print('fetch rc', r.returncode, r.stderr.decode('utf-8', 'replace')[-100:] if r.returncode else '')

def blob(p):
    out = subprocess.run(['git', '-C', GR, 'show', 'origin/main:' + p], capture_output=True, timeout=60)
    return out.stdout

st = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
ord_b = blob('docs/orders.md')
dec_b = blob('docs/decisions.md')
h_ord = hashlib.sha1(ord_b).hexdigest()
h_dec = hashlib.sha1(dec_b).hexdigest()
prev_ord = st.get('last_orders_sha', '')
prev_dec = st.get('last_decisions_sha', '')
print('ORD sha', prev_ord[:12], '->', h_ord[:12])
print('DEC sha', prev_dec[:12], '->', h_dec[:12])

# consume: print only rows NEWER than the last consumed watermark anchors.
# last consumed ORD anchor (r962): mv0001 full-song KF dispatch row (21:3x).
# last consumed DEC anchor: a20664ec content = D-20261010-03/04 era. We dump tail rows and eyeball.
ol = ord_b.decode('utf-8', 'replace').splitlines()
dl = dec_b.decode('utf-8', 'replace').splitlines()
print('=== ORD tail rows (last 8, first 200 chars) ===')
for l in ol[-8:]:
    print(l[:200])
print('=== DEC tail rows (last 6, first 200 chars) ===')
for l in dl[-6:]:
    print(l[:200])
# fleet orders diff
ack = st.get('orders_ack') or {}
ofiles = sorted(f for f in os.listdir('fleet/orders') if f.startswith('O-') and f.endswith('.md'))
unacked = [f for f in ofiles if f not in ack]
print('=== fleet orders: total', len(ofiles), 'unacked', len(unacked), '===')
for f in unacked[:20]:
    print('UNACKED:', f)
