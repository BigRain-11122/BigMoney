import io, json, subprocess, hashlib

# 1) orders diff: origin fleet/orders vs heartbeat orders_ack
orders = subprocess.run(['git', 'ls-tree', '--name-only', 'origin/main', 'fleet/orders/'],
                       capture_output=True, text=True, encoding='utf-8').stdout.split()
hb = json.loads(subprocess.run(['git', 'show', 'origin/main:fleet/machines/bm-a.json'],
                               capture_output=True).stdout.decode('utf-8'))
ack = set(hb.get('orders_ack', []))
unacked = [o for o in orders if o.split('/')[-1] not in ack]
print('orders total:', len(orders), '| acked:', len(ack), '| UNACKED:', unacked if unacked else 'NONE')

# 2) decisions watermark (D-19): python raw-bytes sha256 (r617 law: no PS > redirect)
try:
    d = subprocess.run(['git', '-C', r'K:\Fluxgroup\FluxGroup', 'show', 'origin/main:docs/decisions.md'],
                       capture_output=True).stdout
    sha = hashlib.sha256(d).hexdigest()
    print('decisions sha:', sha[:16], '| stored:', hb.get('last_decisions_sha', '?')[:16],
          '| MATCH' if sha == hb.get('last_decisions_sha') else '| CHANGED')
except Exception as e:
    print('decisions read FAIL:', e)

# 3) group orders.md CEO physical-item section check (same-law read)
try:
    o2 = subprocess.run(['git', '-C', r'K:\Fluxgroup\FluxGroup', 'show', 'origin/main:docs/orders.md'],
                        capture_output=True).stdout.decode('utf-8', errors='replace')
    import re
    m = re.findall(r'2026-10-0[23][^\n]*', o2)
    print('group orders recent lines:', m[-3:] if m else 'none-for-10-02/03')
except Exception as e:
    print('group orders read FAIL:', e)
