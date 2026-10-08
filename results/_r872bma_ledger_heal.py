import hashlib, json, sys

LEGACY = r'logs/iteration-loop/round_reports-bm-a.md'
ROOT = r'round_reports-bm-a.md'

def rows_by_marker(blob, markers):
    lines = blob.split(b'\n')
    out = {}
    for l in lines:
        for mk in markers:
            # row start format: '2026-10-08T...' then '| rNNN bm-a'
            if (b'| ' + mk + b' bm-a') in l[:60]:
                out[mk] = l
    return out

leg = open(LEGACY, 'rb').read()
root = open(ROOT, 'rb').read()

targets = rows_by_marker(leg, [b'r870', b'r871'])
assert set(targets) == {b'r870', b'r871'}, f'marker miss: {list(targets)}'

# idempotency gate: skip rows already present in ROOT (byte-identical)
appended = []
addition = b''
for mk in (b'r870', b'r871'):
    row = targets[mk]
    if row in root:
        print(f'{mk.decode()}: ALREADY in ROOT, skip')
        continue
    addition += row + b'\r\n'
    appended.append(mk.decode())

if addition:
    # ROOT tail terminator normalization: ensure previous content ends with newline
    if not root.endswith(b'\n'):
        addition = b'\r\n' + addition
    with open(ROOT, 'ab') as f:
        f.write(addition)

# verify byte-identical presence
root2 = open(ROOT, 'rb').read()
receipt = {'appended': appended, 'rows': {}}
for mk in (b'r870', b'r871'):
    row = targets[mk]
    receipt['rows'][mk.decode()] = {
        'len': len(row),
        'sha16': hashlib.sha256(row).hexdigest()[:16],
        'in_root': row in root2,
        'in_legacy': row in leg,
    }
print(json.dumps(receipt, ensure_ascii=False, indent=1))
assert all(v['in_root'] and v['in_legacy'] for v in receipt['rows'].values())
print('HEAL OK; ROOT size', len(root), '->', len(root2))
