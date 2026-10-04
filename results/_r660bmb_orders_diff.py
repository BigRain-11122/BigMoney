# r660 bm-b S0.5: orders double-sided set diff (r646 law) + heartbeat sanity
import json, os, glob

files = sorted(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
with open('fleet/machines/bm-b.json', encoding='utf-8') as f:
    hb = json.load(f)
ack = sorted(hb.get('orders_ack', []))
new_orders = [f for f in files if f not in ack]
stale_ack = [a for a in ack if a not in files]
print('orders files:', len(files), '| ack:', len(ack))
print('NEW (unacked):', new_orders if new_orders else 'NONE')
print('STALE ack (file gone):', stale_ack if stale_ack else 'NONE')
print('heartbeat round_no:', hb.get('round_no'), 'epoch type:', type(hb.get('heartbeat_epoch_utc')).__name__)
