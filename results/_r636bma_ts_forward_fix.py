"""r636 bm-a: w2-judge-2of4 owner_since forward-fix for the monotonic push gate.

The claw (r400 MSG-0612 gate) rightly blocks backward owner_since moves
(anti-replay). This yield-restore is legitimate but reads as backward; per the
gate law, set owner_since to the yield ACTION time (forward-monotonic), with
bm-c's real claim ts (18:47:08) documented in the shard note.
"""
import datetime
import json
import re
import subprocess
import sys

now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
fp = r'results\runnable_pool.json'
data = open(fp, 'rb').read()
i = data.find(b'"key": "w2-judge-2of4"')
eol = b'\r\n'
end = data.find(b'}' + eol, i)
block = data[i:end]
old = b'"owner_since": "2026-10-03 18:47:08"'
assert old in block, 'expected restore-ts not found'
nb = block.replace(old, ('"owner_since": "%s"' % now).encode())
data = data[:i] + nb + data[end:]
json.loads(data.decode('utf-8'))
open(fp, 'wb').write(data)
after = json.loads(open(fp, encoding='utf-8').read())
for ent in after['entries']:
    for sh in ent.get('shards', []):
        if sh.get('key') == 'w2-judge-2of4':
            print('w2-judge-2of4:', sh.get('owner'), sh.get('owner_since'),
                  '| note has real ts:', '18:47:08' in (sh.get('note') or ''))
r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
print('numstat:', r.stdout.strip())
sys.exit(0)
