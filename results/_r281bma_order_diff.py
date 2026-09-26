import glob, os, re

files = {os.path.basename(f) for f in glob.glob('fleet/orders/O-*.md')}
raw = open('fleet/machines/bm-a.json', encoding='utf-8').read()
m = re.search(r'"orders_ack": "(.*?)"', raw, re.S)
ack = set(m.group(1).split())
ack_norm = {(a if a.endswith('.md') else a + '.md') for a in ack}
missing = sorted(files - ack_norm)
print('UNACKED:', missing if missing else 'NONE')
