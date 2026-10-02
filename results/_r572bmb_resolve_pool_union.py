import subprocess, json, sys

def stage_bytes(spec):
    r = subprocess.run(['git', 'show', spec], capture_output=True)
    assert r.returncode == 0, r.stderr.decode('utf-8', 'replace')
    return r.stdout

base = [l for l in stage_bytes(':1:results/pool_core_samples.jsonl').split(b'\n') if l.strip()]
ours = [l for l in stage_bytes(':2:results/pool_core_samples.jsonl').split(b'\n') if l.strip()]
theirs = [l for l in stage_bytes(':3:results/pool_core_samples.jsonl').split(b'\n') if l.strip()]
print('base=%d ours=%d theirs=%d' % (len(base), len(ours), len(theirs)))

bset = set(base)
ours_new = [l for l in ours if l not in bset]
theirs_new = [l for l in theirs if l not in bset]
print('ours_new=%d theirs_new=%d' % (len(ours_new), len(theirs_new)))

# r294 dedupe domain = conflict region (new lines only); r570 dict-only gate
seen = set(ours_new)
merged_new = list(ours_new)
for l in theirs_new:
    if l not in seen:
        merged_new.append(l)
        seen.add(l)
bad = 0
for l in merged_new:
    try:
        assert isinstance(json.loads(l.decode('utf-8')), dict)
    except Exception:
        bad += 1
print('merged_new=%d non_dict=%d' % (len(merged_new), bad))
assert bad == 0, 'non-dict line in union set'

out = base + merged_new
with open('results/pool_core_samples.jsonl', 'wb') as f:
    f.write(b'\n'.join(out) + b'\n')

# post-verify: full file all-dict (r570 two-gate)
nbad = 0
for l in out:
    try:
        assert isinstance(json.loads(l.decode('utf-8')), dict)
    except Exception:
        nbad += 1
assert nbad == 0, 'post-verify non-dict lines=%d' % nbad
print('UNION WRITTEN: %d lines total (base %d + new %d), all-dict OK' % (len(out), len(base), len(merged_new)))
