import json, glob, os
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
ack = h.get('orders_ack', [])
print('TYPE', type(ack).__name__)
if isinstance(ack, str):
    ack = ack.split()
files = sorted(glob.glob('fleet/orders/O-*.md'))
names = [os.path.basename(f) for f in files]
ackset = set(ack)
nameset = set(names)
unacked = [n for n in names if n not in ackset]
print('ACK_N', len(ackset), 'FILES_N', len(nameset))
print('UNACKED:')
for n in unacked:
    print(' ', n)
