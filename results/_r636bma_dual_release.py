"""r636 bm-a: dual-shard yield release (w2-judge-2of4 -> bm-c restore; divlowvol-nulls -> null).

w2-judge-2of4: my daemon's 18:47:49 claim yields to bm-c's 18:47:08 first claim
(later-claimant yield law); burn killed 18:49:50, zero pollution verified (no
files written in the 2-min window).
divlowvol-nulls: 6th double-burn claim (18:48:09 race vs my 18:48:03 pin
commit), burn killed 18:49:50, zero rows (mtime 18:45:21 pre-launch).
"""
import json
import subprocess
import sys

fp = r'results\runnable_pool.json'
data = open(fp, 'rb').read()
crlf = data.count(b'\r\n')
lf = data.count(b'\n')
eol = b'\r\n' if crlf * 2 > lf else b'\n'

# --- shard 1: w2-judge-2of4 -> bm-c restore ---
KEY1 = b'"key": "w2-judge-2of4"'
i = data.find(KEY1)
assert i > 0, 'w2 shard not found'
end = data.find(b'}' + eol, i)
block = data[i:end]
assert b'"owner": "bm-a"' in block, 'w2 shard: bm-a claim not found'
nb = block.replace(b'"owner": "bm-a"', b'"owner": "bm-c"')
# fix owner_since: find the bm-a ts (18:47:4x) and replace with bm-c's 18:47:08
import re
m = re.search(rb'"owner_since": "2026-10-03 18:4\d:\d\d"', nb)
if m:
    nb = nb.replace(m.group(0), b'"owner_since": "2026-10-03 18:47:08"')
YIELD = (b" | rel-bm-a-r636 18:50: yield -- bm-a daemon 18:47:49 claim was 41s later than "
         b"bm-c 18:47:08 first claim; bm-a burn killed 18:49:50 zero-pollution; "
         b"bm-c rightful owner")
for anc in (b'checkpoint",', b'note":', b'",'):
    pass
# append yield note to the shard's note field end (anchor = last quote-comma before owner)
if b'rel-bm-a-r636' not in nb:
    # anchor: end of note value -- find note line and append before its closing quote
    mj = re.search(rb'("note": "[^"]*)(")', nb)
    if mj:
        nb = nb[:mj.end(1)] + YIELD + nb[mj.end(1):]
data = data[:i] + nb + data[end:]
json.loads(data.decode('utf-8'))

# --- shard 2: divlowvol-nulls -> null ---
KEY2 = b'"key": "fund-divlowvol-p1-nulls-0of1"'
i2 = data.find(KEY2)
assert i2 > 0
end2 = data.find(b'}' + eol, i2)
block2 = data[i2:end2]
assert b'"owner": "bm-a"' in block2, 'divlowvol shard: bm-a claim not found'
nb2 = block2.replace(b'"owner": "bm-a"', b'"owner": null')
m2 = re.search(rb'"owner_since": "2026-10-03 18:4\d:\d\d"', nb2)
if m2:
    nb2 = nb2.replace(m2.group(0), b'"owner_since": null')
REL2 = (b" | rel-bm-a-r636 18:50: 6th double-burn claim released (18:48:09 daemon re-claim "
        b"racing my 18:48:03 pin commit; burn killed 18:49:50 zero rows, file mtime 18:45:21 "
        b"pre-launch; bm-b canonical burn in flight; fuse division pins on origin both faces)")
if b'rel-bm-a-r636' not in nb2:
    mj2 = re.search(rb'("note": "[^"]*)(")', nb2)
    if mj2:
        nb2 = nb2[:mj2.end(1)] + REL2 + nb2[mj2.end(1):]
data = data[:i2] + nb2 + data[end2:]
json.loads(data.decode('utf-8'))
open(fp, 'wb').write(data)

after = open(fp, 'rb').read()
json.loads(after.decode('utf-8'))
pool = json.loads(after.decode('utf-8'))
for ent in pool['entries']:
    for sh in ent.get('shards', []):
        if sh.get('key') == 'w2-judge-2of4':
            print('w2-judge-2of4 owner:', sh.get('owner'), '| since:', sh.get('owner_since'),
                  '| rel-note:', 'rel-bm-a-r636' in (sh.get('note') or ''))
        if sh.get('key') == 'fund-divlowvol-p1-nulls-0of1':
            print('divlowvol owner:', sh.get('owner'), '| since:', sh.get('owner_since'),
                  '| rel-note:', 'rel-bm-a-r636' in (sh.get('note') or ''))
r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
print('numstat:', r.stdout.strip())
sys.exit(0)
