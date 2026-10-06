import json, os, re

d = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))
acked = set(d.get('orders_ack', []))
orders_dir = 'fleet/orders'
all_o = [f[:-3] for f in os.listdir(orders_dir) if f.startswith('O-') and f.endswith('.md')]
missing = sorted(set(all_o) - acked)
print(json.dumps({'total_orders': len(all_o), 'acked': len(acked), 'unacked': missing}, ensure_ascii=False))
