"""r831 push-race absorb3-pick history 3-way union fix (same recipe as this window's opening leg7)."""
import subprocess, json, io

r = subprocess.run(['git', 'ls-files', '-u'], capture_output=True, text=True, encoding='utf-8')
stages = {}
for ln in r.stdout.splitlines():
    info = ln.split()
    stages.setdefault(info[3], {})[info[2]] = info[1]

P = 'results/saturation_engine/history_bm-a.jsonl'
def catf(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

H2 = [ln for ln in catf(stages[P]['2']).decode('utf-8', 'replace').splitlines() if ln.strip()]
H3 = [ln for ln in catf(stages[P]['3']).decode('utf-8', 'replace').splitlines() if ln.strip()]
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
print(f'WT {len(WT)} -> data {len(wt_data)} (dropped {len(WT)-len(wt_data)} marker/garbage)')

seen = {}
for src in (H2, H3, wt_data):
    for ln in src:
        if ln not in seen:
            seen[ln] = json.loads(ln).get('ts', '')
merged = sorted(seen.keys(), key=lambda ln: seen[ln])
io.open(P, 'wb').write(('\n'.join(merged) + '\n').encode('utf-8'))

chk = [ln for ln in io.open(P, encoding='utf-8').read().splitlines() if ln.strip()]
assert len(chk) == len(merged)
for ln in chk:
    json.loads(ln)
set_all = set(H2) | set(H3) | set(wt_data)
assert set_all <= set(chk)
tss = [json.loads(ln).get('ts') for ln in chk]
non_mono = sum(1 for a, b in zip(tss, tss[1:]) if b and a and b < a)
print(f'history 3-way merge LANDED: {len(chk)} lines, zero-loss PASS, ts-monotone violations={non_mono}')
