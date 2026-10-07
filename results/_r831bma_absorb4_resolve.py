"""r831 push-race absorb4-pick 3-face resolve: :2: side is POLLUTED (marker-staged into 8ea9332bd by add -A),
:3: side = clean absorb4 blob. State/face -> take :3: (only clean side); history -> :3: union worktree data lines."""
import subprocess, json, io

r = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True, encoding='utf-8')
stages = {}
for ln in r.stdout.splitlines():
    info = ln.split()
    stages.setdefault(info[3], {})[info[2]] = info[1]

def catf(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

def has_marker(b):
    return b'<<<<<<<' in b or b'>>>>>>>' in b

# state/face: take :3: (clean) -- verify :2: polluted, :3: clean
for p in ('results/saturation_engine/state_bm-a.json', 'results/saturation_engine/face_bm-a.json'):
    b2, b3 = catf(stages[p]['2']), catf(stages[p]['3'])
    m2, m3 = has_marker(b2), has_marker(b3)
    assert not m3, f'{p}: :3: ALSO polluted?!'
    d = json.loads(b3)
    io.open(p, 'wb').write(b3)
    print(f'{p}: :2: polluted={m2} -> took clean :3: ({len(b3)}B, ts {d.get("last_tick", {}).get("ts") or d.get("ts")})')

# history: :3: union worktree data lines (filter markers)
P = 'results/saturation_engine/history_bm-a.jsonl'
b3 = catf(stages[P]['3'])
assert not has_marker(b3), 'history :3: polluted?!'
H3 = [ln for ln in b3.decode('utf-8', 'replace').splitlines() if ln.strip()]
WT = [ln for ln in io.open(P, encoding='utf-8', errors='replace').read().splitlines() if ln.strip()]

def is_marker(ln):
    return ln.startswith('<<<<<<<') or ln.startswith('=======') or ln.startswith('>>>>>>>')

def is_json(ln):
    try:
        json.loads(ln)
        return True
    except Exception:
        return False

wt_data = [ln for ln in WT if not is_marker(ln) and is_json(ln)]
print(f'history WT {len(WT)} -> data {len(wt_data)}')

seen = {}
for src in (H3, wt_data):
    for ln in src:
        if ln not in seen:
            seen[ln] = json.loads(ln).get('ts', '')
merged = sorted(seen.keys(), key=lambda ln: seen[ln])
with open(P, 'wb') as f:
    for ln in merged:
        f.write((ln + '\n').encode('utf-8'))
chk = [ln for ln in io.open(P, encoding='utf-8').read().splitlines() if ln.strip()]
assert len(chk) == len(merged)
for ln in chk:
    json.loads(ln)
print(f'history merged LANDED: {len(chk)} lines, all parse OK')
