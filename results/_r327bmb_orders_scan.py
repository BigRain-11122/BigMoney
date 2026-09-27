"""r327 bm-b orders double-scan: fleet/orders O-*.md filename set vs heartbeat orders_ack diff (receipt artifact, reused at S7 close scan)."""
import json, glob, io

h = json.load(io.open('fleet/machines/bm-b.json', encoding='utf-8'))
acks = set(h.get('orders_ack') or [])
orders = set(p.replace('\\', '/').split('/')[-1] for p in glob.glob('fleet/orders/O-*.md'))
print('orders_total', len(orders), 'ack_total', len(acks))
print('unreceipted', sorted(orders - acks))
print('ack_extra', sorted(acks - orders))
