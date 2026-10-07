"""r831 leg7: rebuild merged history minus marker residue, parse-verify, zero-loss assert."""
import subprocess, json

def catf(sha):
    return subprocess.run(['git', 'cat-file', '-p', sha], capture_output=True).stdout

H2 = [ln for ln in catf('d90ea4b772bcc4cf4bb59a9ff23a4d124a3d6511').decode('utf-8').splitlines() if ln.strip()]
H3 = [ln for ln in catf('a358c7e2c113ed1dfe9a37cb82da8b80f45f00ba').decode('utf-8').splitlines() if ln.strip()]
with open('results/saturation_engine/history_bm-a.jsonl', 'rb') as f:
    WT = [ln for ln in f.read().decode('utf-8', 'replace').splitlines() if ln.strip()]

def is_marker(ln):
    return ln.startswith('<<<<<<<') or ln.startswith('=======') or ln.startswith('>>>>>>>')

def is_json(ln):
    try:
        json.loads(ln)
        return True
    except Exception:
        return False

# marker residue lives ONLY in WT; drop it (pollution, not data)
wt_data = [ln for ln in WT if not is_marker(ln) and is_json(ln)]
dropped = len(WT) - len(wt_data)
print(f'WT {len(WT)} lines -> {len(wt_data)} data lines ({dropped} marker/garbage dropped)')

seen = {}
for src in (H2, H3, wt_data):
    for ln in src:
        if ln not in seen:
            seen[ln] = json.loads(ln).get('ts', '')
merged = sorted(seen.keys(), key=lambda ln: seen[ln])
print(f'merged union={len(merged)} lines')

with open('results/saturation_engine/history_bm-a.jsonl', 'wb') as f:
    for ln in merged:
        f.write((ln + '\n').encode('utf-8'))

# re-read verify: every line parses, count matches
with open('results/saturation_engine/history_bm-a.jsonl', 'rb') as f:
    chk = [ln for ln in f.read().decode('utf-8').splitlines() if ln.strip()]
assert len(chk) == len(merged)
for ln in chk:
    json.loads(ln)
print('parse-verify PASS')

# zero-loss: all data lines from all three sides present
set_all = set(H2) | set(H3) | set(wt_data)
assert set_all <= set(chk), 'zero-loss FAIL'
assert len(chk) == len(set_all), f'count mismatch {len(chk)} vs {len(set_all)}'
print(f'zero-loss assertion PASS: {len(chk)} lines = 3-way union of data lines')

# ts monotonicity check
tss = [json.loads(ln).get('ts') for ln in chk]
non_mono = sum(1 for a, b in zip(tss, tss[1:]) if b and a and b < a)
print(f'ts monotonicity violations={non_mono}')
