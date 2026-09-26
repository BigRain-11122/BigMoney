import os, glob, json, io
ack = json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))['orders_ack'].split()
files = set(os.path.basename(p) for p in glob.glob('fleet/orders/O-*.md'))
print('orders_on_disk', len(files), 'acked', len(ack))
print('UNACKED:', sorted(files - set(ack)))
print('ACKED_NOT_ON_DISK:', sorted(set(ack) - files))
p = r'C:\Users\Administrator\docs\decisions.md'
print('decisions.md exists:', os.path.exists(p))
if os.path.exists(p):
    lines = open(p, encoding='utf-8').read().splitlines()
    print('decisions total lines:', len(lines))
    print('--- tail 12 ---')
    for l in lines[-12:]:
        print(l[:200])
