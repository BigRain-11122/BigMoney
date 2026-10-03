# r614 bm-b rebase-truncation heal: value nulls.jsonl k-gap (144) filled from churn
# commit blob b63b1b427 (deterministic rng([seed,k]) => byte-identical row), byte-level
# union by k (r570 law: git-anchored, exact line bytes preserved), atomic os.replace,
# contiguity 0..max asserted; re-audited from disk after replace.
import json, os, subprocess

def rows_from_bytes(raw):
    out = {}
    for ln in raw.split(b'\n'):
        if not ln.strip():
            continue
        r = json.loads(ln.decode('utf-8'))
        if not isinstance(r, dict) or 'k' not in r:
            raise SystemExit('non-dict or k-less row: %r' % ln[:80])
        k = int(r['k'])
        if k in out:
            raise SystemExit('duplicate k=%d on input' % k)
        out[k] = ln
    return out

path = 'results/fund_value_p1/nulls.jsonl'
blob = subprocess.run(['git', 'show', 'b63b1b427:results/fund_value_p1/nulls.jsonl'],
                      capture_output=True)
assert blob.returncode == 0, blob.stderr[:200]
git_rows = rows_from_bytes(blob.stdout)

for attempt in range(3):
    disk_raw = open(path, 'rb').read()
    disk_rows = rows_from_bytes(disk_raw)
    missing = [k for k in git_rows if k not in disk_rows]
    merged = dict(disk_rows)
    for k in missing:
        merged[k] = git_rows[k]
    ks = sorted(merged)
    gaps = [(a, b) for a, b in zip(ks, ks[1:]) if b - a > 1]
    assert not gaps, 'gap persists after union: %s' % gaps[:5]
    assert ks[0] == 0, 'first k must be 0'
    out = b'\n'.join(merged[k] for k in ks) + b'\n'
    tmp = path + '.r614heal.tmp'
    with open(tmp, 'wb') as f:
        f.write(out)
    os.replace(tmp, path)
    # re-audit from disk (detect race with live burn appends)
    re_rows = rows_from_bytes(open(path, 'rb').read())
    re_ks = sorted(re_rows)
    re_gaps = [(a, b) for a, b in zip(re_ks, re_ks[1:]) if b - a > 1]
    if not re_gaps:
        print('VALUE heal OK: rows=%d k=0..%d contiguous, filled=%s'
              % (len(re_ks), re_ks[-1], missing))
        break
    print('race detected (attempt %d), re-running union: gaps=%s' % (attempt + 1, re_gaps[:3]))
else:
    raise SystemExit('heal failed after 3 attempts')

# quality file: contiguity audit only (no repair expected -- determinism self-healed)
qpath = 'results/fund_quality_p1/nulls.jsonl'
q_rows = rows_from_bytes(open(qpath, 'rb').read())
q_ks = sorted(q_rows)
q_gaps = [(a, b) for a, b in zip(q_ks, q_ks[1:]) if b - a > 1]
print('QUALITY audit: rows=%d k=0..%d gaps=%s' % (len(q_ks), q_ks[-1], q_gaps[:3] or 'NONE'))
assert not q_gaps, 'quality has unexpected gaps'
print('HEAL_OK')
