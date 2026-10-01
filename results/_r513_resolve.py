import subprocess, json, sys

def blob(p, s):
    return subprocess.check_output(['git', 'show', f':{s}:{p}'])

paths = [
    'results/autofill_state.bm-b.json',
    'results/p1d_gates.json',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
]
# 6 files: my side is newest/superset (asserted in _r513_resolve.py) -> take my blob verbatim
for p in paths:
    out = subprocess.check_output(['git', 'checkout', '--theirs', '--', p])
    raw = open(p, 'rb').read().decode('utf-8-sig')
    if p.endswith('.jsonl'):
        for l in (x for x in raw.replace('\r\n', '\n').split('\n') if x.strip()):
            json.loads(l)
    else:
        json.loads(raw)
    print(f'take-mine OK: {p}')

# pool_core_samples.jsonl: ts-ordered exact-line union (zero loss)
p = 'results/pool_core_samples.jsonl'
base_raw = blob(p, 2).decode('utf-8-sig')
mine_raw = blob(p, 3).decode('utf-8-sig')
nl = '\r\n' if '\r\n' in mine_raw else '\n'
trailing = mine_raw.endswith('\n')
def to_lines(raw):
    return [l for l in raw.replace('\r\n', '\n').split('\n') if l.strip()]
base_lines, mine_lines = to_lines(base_raw), to_lines(mine_raw)
seen, merged = set(), []
def ts_of(l):
    try:
        return json.loads(l).get('ts', '')
    except Exception:
        return ''
for l in base_lines + mine_lines:  # stable seed order
    if l not in seen:
        seen.add(l)
        merged.append(l)
merged.sort(key=ts_of)  # ts-ordered, python sort stable
union_n = len(merged)
expected = len(set(base_lines) | set(mine_lines))
assert union_n == expected, (union_n, expected)
out_txt = nl.join(merged) + (nl if trailing else '')
with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(out_txt)
print(f'{p}: union base={len(base_lines)} mine={len(mine_lines)} -> {union_n} lines (dedupe-exact, ts-ordered, nl={"CRLF" if nl==chr(13)+chr(10) else "LF"})')
# verify reparse
for l in merged:
    json.loads(l)
print('reparse OK')
