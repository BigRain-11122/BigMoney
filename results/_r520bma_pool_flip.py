# r520 bm-a: raw-text surgical pool flip for PERPETUAL-N1-W9-SHARD-9/10/11 (r509 law: no re-serialization)
# Products for 9/10/11 fast-forwarded byte-exact from origin/machine/bm-c-r319; local in-flight shard-9 burn = duplicate, discard on completion.
import json, re, sys

POOL = r'results\runnable_pool.json'
raw = open(POOL, 'rb').read().decode('utf-8')
crlf = '\r\n' if '\r\n' in raw[:2000] else '\n'

flipped = []
for sid in ['PERPETUAL-N1-W9-SHARD-9', 'PERPETUAL-N1-W9-SHARD-10', 'PERPETUAL-N1-W9-SHARD-11']:
    anchor = f'"{sid}"'
    i = raw.find(anchor)
    if i < 0:
        print(f'{sid}: NOT FOUND'); sys.exit(2)
    seg = raw[i:i+500]
    m = re.search(r'"status":\s*"(\w+)"', seg)
    if not m:
        print(f'{sid}: no status near id'); sys.exit(2)
    old = m.group(0)
    if old == '"status": "done"':
        print(f'{sid}: already done'); continue
    # replace only this first occurrence after the id anchor
    abs_start = i + m.start()
    abs_end = i + m.end()
    raw = raw[:abs_start] + '"status": "done"' + raw[abs_end:]
    flipped.append((sid, old))

open(POOL, 'wb').write(raw.encode('utf-8'))

# verify: parse + targeted assertion
p = json.loads(open(POOL, 'rb').read().decode('utf-8'))
for e in p['entries']:
    if e['id'] in ('PERPETUAL-N1-W9-SHARD-9', 'PERPETUAL-N1-W9-SHARD-10', 'PERPETUAL-N1-W9-SHARD-11'):
        print(e['id'], '->', e.get('status'))
print('flip count:', len(flipped), '| crlf detected:', crlf == '\r\n')
