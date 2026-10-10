# r963 D-19 dual watermark check: group decisions.md + orders.md hash compare (fresh origin read, zero tree touch)
import subprocess, hashlib, json, io

GR = r'K:\Fluxgroup\FluxGroup'
subprocess.run(['git', '-C', GR, 'fetch', 'origin'], capture_output=True, timeout=120)

def sha(b): return hashlib.sha256(b).hexdigest()

st = json.load(io.open('fleet/machines/bm-a.json', encoding='utf-8'))
prev_dec, prev_ord = st.get('last_decisions_sha'), st.get('last_orders_sha')

dec = subprocess.run(['git', '-C', GR, 'show', 'origin/main:docs/decisions.md'], capture_output=True, timeout=60).stdout
orders = subprocess.run(['git', '-C', GR, 'show', 'origin/main:docs/orders.md'], capture_output=True, timeout=60).stdout
h_dec, h_ord = sha(dec), sha(orders)
print('decisions:', prev_dec[:12], '->', h_dec[:12], 'CHANGED' if h_dec != prev_dec else 'unchanged')
print('orders:   ', prev_ord[:12], '->', h_ord[:12], 'CHANGED' if h_ord != prev_ord else 'unchanged')

# if changed, dump the tail lines for consumption check
if h_ord != prev_ord:
    lines = orders.decode('utf-8', errors='replace').splitlines()
    print('--- orders.md tail 12 ---')
    for l in lines[-12:]: print(l[:180])
if h_dec != prev_dec:
    lines = dec.decode('utf-8', errors='replace').splitlines()
    print('--- decisions.md tail 15 ---')
    for l in lines[-15:]: print(l[:180])
