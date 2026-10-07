import json, hashlib, os, subprocess, io

# 1) orders diff: fleet/orders/*.md minus heartbeat orders_ack
ack = set(json.load(open('fleet/machines/bm-a.json', encoding='utf-8')).get('orders_ack', []))
all_orders = sorted(f for f in os.listdir('fleet/orders') if f.endswith('.md'))
unacked = [f for f in all_orders if f not in ack]
print('UNACKED_ORDERS:', unacked if unacked else 'NONE')

# 2) group decisions watermark: local FluxGroup fallback (K: absent per D-20261004-02(3))
GT = r'C:\Users\sjs20\Desktop\FluxGroup'
subprocess.run(['git', '-C', GT, 'fetch', 'origin'], capture_output=True, timeout=120)
dec = subprocess.run(['git', '-C', GT, 'show', 'origin/main:docs/decisions.md'],
                     capture_output=True, timeout=60)
dec_bytes = dec.stdout
dec_sha = hashlib.sha256(dec_bytes).hexdigest()
orders = subprocess.run(['git', '-C', GT, 'show', 'origin/main:docs/orders.md'],
                        capture_output=True, timeout=60)
orders_sha = hashlib.sha256(orders.stdout).hexdigest()

state = json.load(open('state-bm-a.json', encoding='utf-8'))
prev_dec = state.get('last_decisions_sha')
prev_ord = state.get('last_orders_sha')
print('DEC_SHA_CUR:', dec_sha)
print('DEC_SHA_PREV:', prev_dec)
print('DEC_CHANGED:', dec_sha != prev_dec)
print('ORD_SHA_CUR:', orders_sha)
print('ORD_SHA_PREV:', prev_ord)
print('ORD_CHANGED:', orders_sha != prev_ord)

# 3) local not-at-origin count for bigmoney repo
behind = subprocess.run(['git', 'rev-list', '--count', 'HEAD..origin/main'],
                         capture_output=True, text=True, cwd='.')
print('NOT_AT_ORIGIN:', behind.stdout.strip())
