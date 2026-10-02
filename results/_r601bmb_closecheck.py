import json, os, subprocess

# orders diff (closeout double-scan leg 2)
ack = set(json.load(open('fleet/machines/bm-b.json', encoding='utf-8'))['orders_ack'])
files = set(os.listdir('fleet/orders'))
unack = sorted(f for f in files if f not in ack and f.startswith('O-'))
print('unacked orders:', unack if unack else 'NONE')

# D-face scan (r388 XY two-column law) before any add -A
r = subprocess.run(['git', 'status', '--porcelain'], capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
d_rows = [l for l in r.stdout.splitlines() if l.strip() and 'D' in l[:2]]
print('D rows:', len(d_rows))
for l in d_rows[:10]:
    print(' ', l)
mods = [l for l in r.stdout.splitlines() if l.strip() and '?' not in l[:2]]
untracked = [l for l in r.stdout.splitlines() if l.startswith('??')]
print('tracked mods:', len(mods), 'untracked:', len(untracked))
for l in untracked:
    print(' ??', l[3:])
