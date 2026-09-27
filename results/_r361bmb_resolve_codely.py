"""_r361bmb_resolve_codely -- finish r360 storm replay: CODELY.md memory-union.

Classifier verdict: memory-union, refined recipe (r311/D-20260927-09):
merge-base prefix-identity assertion on BOTH sides, then DIRECT-CONCAT
suffixes: new = base + ours-suffix + theirs-suffix, entries verbatim,
NO line-level dedupe. Fail-closed: prefix assertion failure = manual review.
Byte math must balance: len(new) == len(base)+len(sA)+len(sB).
"""
import subprocess
import sys

PATH = 'CODELY.md'


def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'],
                       capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'stage {stage} read fail: {r.stderr[:200]!r}')
    return r.stdout


base = blob(1, PATH)
ours = blob(2, PATH)
theirs = blob(3, PATH)

# Manual-review verdict (r311 fail-closed trigger -> diagnosed this window):
# theirs' ONLY in-place edit = UTF-8 BOM stripped at byte 0 (formatting face,
# r360 session wrote without BOM); both sides are pure-append after BOM
# normalization. Union keeps the BOM (canonical format of base+ours).
BOM = b'\xef\xbb\xbf'
assert base.startswith(BOM) and ours.startswith(BOM)
assert not theirs.startswith(BOM)
core = base[3:]
assert ours.startswith(base), 'ours not pure-append of base (r311)'
assert theirs.startswith(core), 'theirs not pure-append after BOM strip (r311)'

sa = ours[len(base):]
sb = theirs[len(core):]
merged = BOM + core + sa + sb

if b'<<<<<<<' in merged or b'>>>>>>>' in merged or b'=======' in merged:
    raise SystemExit('FAIL: conflict marker found in merged bytes')

with open(PATH, 'wb') as fh:
    fh.write(merged)

# zero-loss byte math: BOM + core + ours-suffix + theirs-suffix
assert len(merged) == 3 + len(core) + len(sa) + len(sb)
print(f'BOM+core={3+len(core)}B ours-suffix={len(sa)}B theirs-suffix={len(sb)}B '
      f'merged={len(merged)}B math_ok=True')
print(f'ours-suffix head: {sa[:80]!r}')
print(f'theirs-suffix head: {sb[:80]!r}')
sys.exit(0)
