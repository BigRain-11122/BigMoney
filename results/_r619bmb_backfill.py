"""r619 bm-b: r614 cure — k-union/ts-union backfill of truncation-lost lines, atomic write, asserts.

Lost during interrupted-pick replay checkout (r614 live-write truncation):
  - fund_value_p1/nulls.jsonl  k=231   (only copy: churn pick blob a9c3d35eb)
  - fund_quality_p1/nulls.jsonl k=136  (only copy: churn pick blob 5952f0e3b)
  - saturation_engine/history_bm-b.jsonl ts=14:26:05 (only copy: 5952f0e3b; inside current rolling window)
divlowvol: complete set 0..45 with 3 cosmetic adjacent swaps (pre-existing) — no action.
After backfill the worktree becomes a true superset of the 2 remaining churn picks
=> r543 quit-gate satisfied with zero loss.
"""
import subprocess, json, os, sys

def blob(rev, path):
    r = subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True)
    if r.returncode != 0:
        sys.exit(f'FATAL: cannot read {rev}:{path}')
    return r.stdout.decode('utf-8', 'replace')

def jlines(text):
    return [l for l in text.strip().splitlines() if l.strip()]

def atomic_write(path, lines):
    tmp = path + '.r619tmp'
    with open(tmp, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(lines) + '\n')
    os.replace(tmp, path)

def eol_style(text):
    return '\r\n' if '\r\n' in text[:2000] else '\n'

fails = []

# 1) fund_value k=231 backfill
p = 'results/fund_value_p1/nulls.jsonl'
raw = open(p, encoding='utf-8', newline='').read()
eol = eol_style(raw)
src = [l for l in jlines(blob('a9c3d35eb', p)) if json.loads(l)['k'] == 231]
assert len(src) == 1, f'expect exactly 1 k=231 source line, got {len(src)}'
wt = jlines(raw)
if not any(json.loads(l)['k'] == 231 for l in wt):
    idx = next(i for i, l in enumerate(wt) if json.loads(l)['k'] > 231)
    wt.insert(idx, src[0])
    atomic_write(p, wt)
ks = [json.loads(l)['k'] for l in jlines(open(p, encoding='utf-8').read())]
ok = ks == sorted(ks) and ks == list(range(0, ks[-1] + 1))
backfill_line = json.loads(src[0])
same = any(json.loads(l) == backfill_line for l in jlines(open(p, encoding='utf-8').read()))
print(('PASS' if ok and same else 'FAIL'), 'fund_value k=231 backfill + full contiguity 0..%d' % ks[-1])
if not (ok and same):
    fails.append(p)

# 2) fund_quality k=136 backfill
p = 'results/fund_quality_p1/nulls.jsonl'
raw = open(p, encoding='utf-8', newline='').read()
src = [l for l in jlines(blob('5952f0e3b', p)) if json.loads(l)['k'] == 136]
assert len(src) == 1
wt = jlines(raw)
if not any(json.loads(l)['k'] == 136 for l in wt):
    idx = next(i for i, l in enumerate(wt) if json.loads(l)['k'] > 136)
    wt.insert(idx, src[0])
    atomic_write(p, wt)
ks = [json.loads(l)['k'] for l in jlines(open(p, encoding='utf-8').read())]
ok = ks == sorted(ks) and ks == list(range(0, ks[-1] + 1))
same = any(json.loads(l) == json.loads(src[0]) for l in jlines(open(p, encoding='utf-8').read()))
print(('PASS' if ok and same else 'FAIL'), 'fund_quality k=136 backfill + full contiguity 0..%d' % ks[-1])
if not (ok and same):
    fails.append(p)

# 3) engine history ts=14:26:05 backfill (within current rolling window)
p = 'results/saturation_engine/history_bm-b.jsonl'
raw = open(p, encoding='utf-8', newline='').read()
src = [l for l in jlines(blob('5952f0e3b', p)) if json.loads(l)['ts'] == '2026-10-03T14:26:05+08:00']
assert len(src) == 1
wt = jlines(raw)
if not any(json.loads(l)['ts'] == '2026-10-03T14:26:05+08:00' for l in wt):
    idx = next(i for i, l in enumerate(wt) if json.loads(l)['ts'] > '2026-10-03T14:26:05+08:00')
    wt.insert(idx, src[0])
    atomic_write(p, wt)
ts = [json.loads(l)['ts'] for l in jlines(open(p, encoding='utf-8').read())]
ok = ts == sorted(ts) and '2026-10-03T14:26:05+08:00' in ts
print(('PASS' if ok else 'FAIL'), f'engine history 14:26:05 backfill, n={len(ts)}, span {ts[0]}..{ts[-1]}')
if not ok:
    fails.append(p)

# 4) divlowvol: set-complete cosmetic swaps — verify only
ks = sorted(json.loads(l)['k'] for l in jlines(open('results/fund_divlowvol_p1/nulls.jsonl', encoding='utf-8').read()))
ok = ks == list(range(0, ks[-1] + 1))
print(('PASS' if ok else 'FAIL'), f'divlowvol set-complete 0..{ks[-1]} (3 cosmetic adjacent swaps, no loss, no action)')
if not ok:
    fails.append('divlowvol')

print('SUMMARY:', 'ALL PASS' if not fails else f'FAIL: {fails}')
sys.exit(1 if fails else 0)
