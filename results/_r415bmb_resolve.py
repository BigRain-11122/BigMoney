"""r415 bm-b resolver: 20-UU same-window S6 twin faces vs bm-a r420 (rebase replay).
Classifier: 10 classified + 10 UNKNOWN manual-qualified per SKILL.md + r404/r408 precedents.
Stage semantics (pit-75/76): stage2 = base (origin/bm-a side), stage3 = mine replayed.
take-NEW law: t3>t2 -> stage3; t2>t3 -> stage2; tie -> stage2 (r140).
Rolling-ledgers: union zero-loss. CODELY: memory-union with cold-archive awareness
(my side already migrated 4 verbose entries verbatim to archive -> drop from hot only).
Archive: append-union both sides' new lines. md twins follow json twin side.
Zero-PS-redirect: all blob reads via subprocess bytes (r209).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r'20\d\d-\d\d-\d\d[T ]\d\d:\d\d:\d\d')


def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f'stage {stage} read fail {path}: {r.stderr[:120]}')
    return r.stdout


def max_ts(b):
    m = TS_RE.findall(b.decode('utf-8', errors='replace'))
    return max(m) if m else ''


def take_new_json(path):
    b2, b3 = blob(2, path), blob(3, path)
    t2, t3 = max_ts(b2), max_ts(b3)
    win = 3 if t3 > t2 else 2  # tie -> stage2 (r140)
    data = json.loads((b3 if win == 3 else b2).decode('utf-8'))
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(f'{path}: take stage{win} (t2={t2} t3={t3})')
    return win


# ---------- 1) snapshots + doc twins + js wrapper: take-NEW ----------
SNAP_JSON = [
    'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
    'results/prospect_promotion/_summary.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'docs/daily_report/REPORT-2026-09-29.json',
    'docs/live_usage/LIVE-2026-09-29.json',
    'docs/live_usage/LIVE-latest.json',
]
sides = {}
for p in SNAP_JSON:
    sides[p] = take_new_json(p)

# md twins follow their json twin side
for j, m in [
    ('docs/daily_report/REPORT-2026-09-29.json', 'docs/daily_report/REPORT-2026-09-29.md'),
    ('docs/live_usage/LIVE-2026-09-29.json', 'docs/live_usage/LIVE-2026-09-29.md'),
    ('docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md'),
]:
    win = sides[j]
    raw = blob(win, m)
    with open(m, 'wb') as fh:
        fh.write(raw)
    print(f'{m}: follow json twin -> stage{win} ({len(raw)}B)')

# dashboard_status.js: js-wrapper whole-bytes take-side (R209: never json.dumps rewrite)
b2, b3 = blob(2, 'results/dashboard_status.js'), blob(3, 'results/dashboard_status.js')
t2, t3 = max_ts(b2), max_ts(b3)
win = 3 if t3 > t2 else 2
raw = b3 if win == 3 else b2
assert b'window.DASH_DATA' in raw, 'js wrapper missing'
with open('results/dashboard_status.js', 'wb') as fh:
    fh.write(raw)
print(f'results/dashboard_status.js: wrapper-preserved take stage{win} (t2={t2} t3={t3})')

# ---------- 2) rolling-ledgers: union zero-loss ----------
for path, hist_key in [('results/compute_audit.json', 'history'),
                       ('results/regime_state.json', 'history')]:
    d2 = json.loads(blob(2, path).decode('utf-8'))
    d3 = json.loads(blob(3, path).decode('utf-8'))
    h2 = d2.get(hist_key) or []
    h3 = d3.get(hist_key) or []
    if isinstance(h2, dict):
        keys = list(h2.keys() | h3.keys()) if sys.version_info >= (3, 9) else list(set(h2) | set(h3))
        union = {k: (h3.get(k) or h2.get(k)) for k in keys}
        n_union = len(union)
        merged = union
    else:
        seen, merged = [], []
        for row in h3 + h2:  # mine first, then base rows not already present
            key = json.dumps(row, sort_keys=True, ensure_ascii=False)
            if key not in seen:
                seen.append(key)
                merged.append(row)
        n_union = len(merged)
    base_newer = max_ts(blob(2, path)) >= max_ts(blob(3, path))
    out = d2 if base_newer else d3  # state fields take-NEW by overall ts
    out[hist_key] = merged
    n_src = len(set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in h2)
                | set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in h3)) \
        if not isinstance(h2, dict) else len(set(h2) | set(h3))
    assert n_union == n_src, f'{path}: union count mismatch {n_union} != {n_src}'
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    print(f'{path}: ledger union {n_union} rows zero-loss, state fields take-{"stage2" if base_newer else "stage3"}')

# ---------- 3) CODELY.md memory-union with cold-archive awareness ----------
c2 = blob(2, 'CODELY.md').decode('utf-8').splitlines(keepends=True)
c3 = blob(3, 'CODELY.md').decode('utf-8').splitlines(keepends=True)
arch3 = blob(3, 'research/memory-archive/202609.md').decode('utf-8')
set3 = set(c3)
kept_new = [l for l in c2 if l not in set3 and l not in arch3]  # bm-a new entries not in mine nor archived
out_lines = c3[:]  # my integrated side as base (4 verbose already cold-archived by me)
# insert bm-a genuinely-new lines before the closing tail (keep section coherence):
if kept_new:
    idx = max(i for i, l in enumerate(out_lines) if l.strip())
    out_lines = out_lines[:idx] + kept_new + out_lines[idx:]
merged_codely = ''.join(out_lines)
assert '\ufffd' not in merged_codely
with open('CODELY.md', 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(merged_codely)
import os
print(f'CODELY.md: memory-union base=stage3(integrated) + {len(kept_new)} bm-a-new lines, '
      f'size={os.path.getsize("CODELY.md")}B; bm-a lines dropped-as-archived='
      f'{sum(1 for l in c2 if l not in set3 and l in arch3)}')

# ---------- 4) archive 202609.md append-union ----------
a2 = blob(2, 'research/memory-archive/202609.md').decode('utf-8')
a3 = blob(3, 'research/memory-archive/202609.md').decode('utf-8')
if a2.startswith(a3[:200]) or a3 in a2:
    out_arch = a2
elif a2 in a3:
    out_arch = a3
else:
    set2lines = set(a2.splitlines())
    mine_only = [l for l in a3.splitlines() if l not in set2lines]
    out_arch = a2 + ('\n' if not a2.endswith('\n') else '') + '\n'.join(mine_only) + '\n'
for probe in ('r415 bm-b', '九十四批'):
    assert probe in out_arch, f'archive lost my content: {probe}'
with open('research/memory-archive/202609.md', 'w', encoding='utf-8', newline='\n') as fh:
    fh.write(out_arch)
print(f'archive 202609.md: union OK {len(out_arch)}B (my section present verbatim)')

print('RESOLVER DONE: 20 faces resolved, parse-validated, zero-loss asserted')
