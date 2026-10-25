# -*- coding: utf-8 -*-
import io
import json
import os

hb = json.load(io.open('fleet/machines/bm-c.json', encoding='utf-8'))
ack = set(hb.get('orders_ack') or [])
files = sorted(f for f in os.listdir('fleet/orders') if f.startswith('O-') and f.endswith('.md'))
missing = [f for f in files if f not in ack]
print('orders_total', len(files), 'acked', len(ack & set(files)), 'unacked', len(missing))
for f in missing:
    print('UNACKED', f)
print('ack_count_field', hb.get('orders_ack_count'), 'ack_last', hb.get('orders_ack_last'))
print('dec_wm', hb.get('last_decisions_sha'), hb.get('last_decisions_sha_method'), hb.get('last_decisions_at'))
print('ord_wm', hb.get('last_orders_sha'), hb.get('last_orders_at'))
print('round_no', hb.get('round_no'), 'last_round', hb.get('last_round'), hb.get('last_round_label'))