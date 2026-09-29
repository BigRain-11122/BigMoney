import subprocess, json

def show(rev, path):
    return subprocess.run(['git', 'show', f'{rev}:{path}'], capture_output=True).stdout.decode('utf-8')

MINE = 'a108ca779'   # stage3 = replayed bm-b r437 close
ORIG = '26d0d8dbb'   # stage2 = origin head (bm-c r232 close)
W = lambda p, s: open(p, 'w', encoding='utf-8', newline='').write(s)

uu = [l[3:] for l in subprocess.run(['git', 'status', '--porcelain'], capture_output=True).stdout.decode().splitlines() if l.startswith('UU')]
assert len(uu) == 14, uu

# --- 1) CODELY.md: memory-union = my re-arch version + bm-c's new entry inserted before my r437 line (chronology) ---
o_lines = show(ORIG, 'CODELY.md').split('\n')
b_lines = set(subprocess.run(['git', 'show', f'd2f71a4e2:CODELY.md'], capture_output=True).stdout.decode('utf-8').split('\n'))
o_new = [l for l in o_lines if l not in b_lines and l.strip()]
m_text = show(MINE, 'CODELY.md')
assert len(o_new) == 1, o_new
bm_c_line = o_new[0]
assert bm_c_line.startswith('- [2026-09-29 18:2x r232 bm-c]'), bm_c_line[:80]
m_lines = m_text.split('\n')
r437_idx = [i for i, l in enumerate(m_lines) if l.startswith('- [2026-09-29 18:3x r437 bm-b]')]
assert len(r437_idx) == 1
m_lines.insert(r437_idx[0], bm_c_line)
merged = '\n'.join(m_lines)
# zero-loss: every origin-new line + every mine-new line present
assert bm_c_line in merged
W('CODELY.md', merged)
import os
print('CODELY.md union ok, size:', os.path.getsize('CODELY.md'))

# --- 2) same-day idempotent regen docs + snapshots + token: take-new (mine = newest generated ts) ---
take_new = [
    'docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md',
    'docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/update_status.json',
    'results/regime_state.json', 'results/token_usage.json',
]
for p in take_new:
    t = show(MINE, p)
    if p.endswith('.json'):
        json.loads(t)  # parse validation before write-back (r185 law)
    W(p, t)
    print('take-new (mine):', p)

# --- 3) compute_audit.json: rolling-ledger union (202-row precedent) + latest take-new ---
o = json.loads(show(ORIG, 'results/compute_audit.json'))
m = json.loads(show(MINE, 'results/compute_audit.json'))
oh, mh = o['history'], m['history']
key = lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False)
union, seen = [], set()
for r in sorted(oh + mh, key=lambda r: r.get('ts', '')):
    k = key(r)
    if k not in seen:
        seen.add(k)
        union.append(r)
assert len(union) == len(set(map(key, oh)) | set(map(key, mh)))
out = dict(m)  # latest + all scalar fields = take-new (mine newer ts)
out['history'] = union
W('results/compute_audit.json', json.dumps(out, ensure_ascii=False, indent=1) + '\n')
json.loads(open('results/compute_audit.json', encoding='utf-8').read())
print('compute_audit union rows:', len(union), '(origin', len(oh), '+ mine', len(mh), ', common', len(seen) - len(union) + len(oh) + len(mh) - len(union), ')')

# --- 4) verify all resolved json parse + stage ---
resolved = ['CODELY.md'] + take_new + ['results/compute_audit.json']
assert set(resolved) == set(uu), set(uu) ^ set(resolved)
for p in resolved:
    if p.endswith('.json'):
        json.loads(open(p, encoding='utf-8').read())
subprocess.run(['git', 'add'] + resolved, check=True)
print('ALL 14 RESOLVED + STAGED')
