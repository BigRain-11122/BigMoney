"""r555 helper: resolve pool_core_samples.jsonl conflict (r294 union domain law)."""
import subprocess

PATH = 'results/pool_core_samples.jsonl'
data = open(PATH, 'rb').read().decode('utf-8')
marker_count = data.count('<<<<<<<') + data.count('=======') + data.count('>>>>>>>')
print('markers:', marker_count)

# capture conflict blocks
out_lines = []
i = 0
lines = data.splitlines(keepends=True)
mode = 'normal'
block_mine, block_theirs = [], []
resolved = []
for ln in lines:
    if ln.startswith('<<<<<<<'):
        mode = 'mine'
        continue
    if ln.startswith('======='):
        mode = 'theirs'
        continue
    if ln.startswith('>>>>>>>'):
        mode = 'normal'
        # union: mine first, then theirs non-duplicate lines (r294: dedupe in conflict zone ONLY)
        seen = set(block_mine)
        for t in block_theirs:
            if t not in seen:
                resolved.extend([t])
                seen.add(t)
        out_lines.extend(block_mine)
        out_lines.extend([t for t in block_theirs if t in set(block_mine) is False and t not in set(block_mine)])
        # simpler: out_lines already has mine; append theirs-not-in-mine
        block_mine, block_theirs = [], []
        continue
    if mode == 'mine':
        block_mine.append(ln)
    elif mode == 'theirs':
        block_theirs.append(ln)
    else:
        out_lines.append(ln)

# redo cleanly (the above got tangled) -- rebuild:
out_lines = []
mode = 'normal'
block_mine, block_theirs = [], []
for ln in lines:
    if ln.startswith('<<<<<<<'):
        mode = 'mine'; continue
    if ln.startswith('======='):
        mode = 'theirs'; continue
    if ln.startswith('>>>>>>>'):
        mine_set = set(block_mine)
        out_lines.extend(block_mine)
        for t in block_theirs:
            if t not in mine_set:
                out_lines.append(t)
        mode = 'normal'; block_mine, block_theirs = [], []
        continue
    if mode == 'mine':
        block_mine.append(ln)
    elif mode == 'theirs':
        block_theirs.append(ln)
    else:
        out_lines.append(ln)

new = ''.join(out_lines)
# verify: no markers left, json-per-line valid
assert '<<<<<<<' not in new and '>>>>>>>' not in new and not any(
    l.startswith('=======') for l in new.splitlines()), 'markers remain'
import json
for l in new.splitlines():
    if l.strip():
        json.loads(l)
print('resolved lines:', len(new.splitlines()), '| all lines json-valid')
open(PATH, 'wb').write(new.encode('utf-8'))
print('written')
