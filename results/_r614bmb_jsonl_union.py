# r614 bm-b pool_core_samples.jsonl merge: r570 domain law -- origin blob as base,
# local dict-only rows union-appended, byte-faithful lines, order-preserving.
import subprocess, json

def raw_lines(ref):
    r = subprocess.run(['git', 'show', ref], capture_output=True)
    assert r.returncode == 0, (ref, r.stderr[:200])
    return [ln for ln in r.stdout.split(b'\n') if ln.strip()]

mb = subprocess.run(['git', 'merge-base', 'HEAD', 'origin/main'],
                    capture_output=True, text=True).stdout.strip()
base_l = raw_lines(mb + ':results/pool_core_samples.jsonl')
mine_l = raw_lines('HEAD:results/pool_core_samples.jsonl')
theirs_l = raw_lines('origin/main:results/pool_core_samples.jsonl')

def typegate(lines, tag):
    for ln in lines:
        v = json.loads(ln.decode('utf-8'))
        assert isinstance(v, dict), 'non-dict row in %s: %r' % (tag, ln[:80])
    return set(lines)

base_s = typegate(base_l, 'base')
mine_s = typegate(mine_l, 'mine')
theirs_s = typegate(theirs_l, 'theirs')

out_lines = list(theirs_l)                       # origin truth order first
for ln in mine_l:                                # local-only rows appended
    if ln not in theirs_s:
        out_lines.append(ln)
for ln in base_l:                                # safety: any base-only rows re-added
    if ln not in theirs_s and ln not in set(out_lines):
        out_lines.append(ln)

dup = len(out_lines) - len(set(out_lines))
assert dup == 0, 'duplicate lines in union result'
with open('results/pool_core_samples.jsonl', 'wb') as f:
    f.write(b'\n'.join(out_lines) + b'\n')
print('pool_core_samples union OK: base=%d mine=%d theirs=%d -> out=%d '
      '(local-new=%d)' % (len(base_l), len(mine_l), len(theirs_l), len(out_lines),
                          sum(1 for ln in mine_l if ln not in theirs_s)))
