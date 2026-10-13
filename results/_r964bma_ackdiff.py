import io, json, os, re, glob

hb_path = 'fleet/machines/bm-a.json'
hb = json.load(io.open(hb_path, encoding='utf-8'))
ack = hb.get('orders_ack') or []
ack_set = set(ack)
files = sorted(glob.glob('fleet/orders/O-*.md'))
names = {os.path.basename(f).replace('.md', '') for f in files}
unacked = sorted(names - ack_set)
print('fleet O-files:', len(names), '| acked:', len(ack_set), '| unacked:', len(unacked))
for u in unacked:
    print('UNACKED:', u)
