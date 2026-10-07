import json, os, glob

# GBK-tolerant read (pit-encoding law)
s = json.load(open('state.json', encoding='utf-8', errors='replace'))
print('state round_no =', s.get('round_no'))

h = json.load(open('fleet/machines/bm-b.json', encoding='utf-8', errors='replace'))
acked = set(h.get('orders_ack', []))
orders = sorted(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
unacked = [o for o in orders if o not in acked]
print('orders total =', len(orders), 'my acked =', len(acked & set(orders)))
print('UNACKED for bm-b duty:', unacked if unacked else 'NONE')

# decisions watermark (D-19) check
print('last_decisions_sha =', str(s.get('last_decisions_sha'))[:20])
