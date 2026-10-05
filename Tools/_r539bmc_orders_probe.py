# r539 bm-c S0.5 orders strict-diff probe (round-start scan; close scan is the second face)
import json, os, glob
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
files = sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, 'fleet', 'orders', '*.md')))
hb = json.load(open(os.path.join(ROOT, 'fleet', 'machines', 'bm-c.json'), encoding='utf-8-sig'))
ack = set(hb.get('orders_ack') or [])
o_files = [f for f in files if f.startswith('O-')]
unacked = [f for f in o_files if f not in ack]
ghost = [a for a in sorted(ack) if a not in files and a != 'README.md']
print('ORDERS_FILES=%d O_FILES=%d ACKED=%d UNACKED=%d' % (len(files), len(o_files), len(ack), len(unacked)))
for f in unacked:
    print('UNACKED: ' + f)
for g in ghost:
    print('GHOST_ACK: ' + g)
print('PROBE_RC=' + ('0' if not unacked else '1'))
