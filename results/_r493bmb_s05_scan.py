import json, os, hashlib, subprocess, glob

# 1) Orders diff: fleet/orders/*.md vs heartbeat orders_ack
hb = json.load(open('fleet/machines/bm-b.json'))
acked = set(hb.get('orders_ack', []))
orders = set(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
missing = sorted(orders - acked)
print('orders on disk:', len(orders), '| acked:', len(acked), '| UNACKED:', missing if missing else 'EMPTY (double-scan basis)')

# 2) state.json D-19 watermark
st = json.load(open('state.json'))
print('last_decisions_sha:', st.get('last_decisions_sha'), '| at:', st.get('last_decisions_at'))

# 3) D-19 fresh read via temp partial clone (r481 bm-b recipe), raw-bytes hash (r292 law)
tmp = os.path.join(os.environ.get('TEMP', '.'), 'fg-dec-bmb')
if not os.path.exists(tmp):
    r = subprocess.run(['git', 'clone', '--depth', '1', '--filter=blob:none', '--no-checkout',
                        'git@github.com:BigRain-11122/FluxGroup.git', tmp], capture_output=True, text=True)
    print('clone rc:', r.returncode)
subprocess.run(['git', '-C', tmp, 'fetch', 'origin'], capture_output=True)
raw = subprocess.check_output(['git', '-C', tmp, 'show', 'origin/main:docs/decisions.md'])
new_sha = hashlib.sha256(raw).hexdigest().upper()
print('decisions.md fresh sha256:', new_sha)
if new_sha == (st.get('last_decisions_sha') or '').upper():
    print('D-19: UNCHANGED -> zero action')
else:
    print('D-19: CHANGED -> must consume 派工通告板 rows')
    # extract tail: new lines since watermark = show last portion for inspection
    txt = raw.decode('utf-8', 'replace')
    lines = txt.splitlines()
    print('--- decisions.md tail 40 lines ---')
    print('\n'.join(lines[-40:]))
# 4) CEO physical-items area in docs/orders.md
try:
    raw2 = subprocess.check_output(['git', '-C', tmp, 'show', 'origin/main:docs/orders.md'])
    txt2 = raw2.decode('utf-8', 'replace')
    print('--- orders.md tail 30 lines (CEO physical items) ---')
    print('\n'.join(txt2.splitlines()[-30:]))
except Exception as e:
    print('orders.md read ERR:', e)
