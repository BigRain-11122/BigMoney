# -*- coding: utf-8 -*-
"""r349 bm-b storm resolver (r346 canon single-process atomic):
1) snapshot all UU stage blobs up-front (tick-race minimization, r335/r351 awareness)
2) per-file recipe routing (classifier 15/15 GREEN):
   - snapshot family x10: hardened deep-ts probe on STAGED blobs, take-new whole side
   - daily_report twins: same-side take-new via .json probe
   - dashboard_status.js: whole-side bytes via inner ts
   - compute_audit / regime_state: ledger union zero-loss + take-new state
   - CODELY.md: stage-1 merge-base prefix-identity assertion BOTH sides, then
     direct-concat appended suffixes (D-20260927-09: NO line-level dedupe)
3) parse-verify every JSON before write-back; add; rebase --continue; push.
"""
import json, subprocess, sys, re, os

def run(args, **kw):
    return subprocess.run(args, capture_output=True, **kw)

# ---------- 0) snapshot stages ----------
uu = run(['git', 'ls-files', '-u']).stdout.decode('utf-8').splitlines()
stages = {}
for ln in uu:
    parts = ln.split('\t')
    meta, path = parts[0], parts[1]
    mode, h, st = meta.split()
    stages.setdefault(path, {})[int(st)] = h
print('UU files:', len(stages))

def blob(h):
    r = run(['git', 'cat-file', 'blob', h])
    if r.returncode != 0 or not r.stdout:
        print('FATAL blob read', h[:12]); sys.exit(1)
    return r.stdout  # bytes

snaps = {}
for p, sh in stages.items():
    snaps[p] = {st: blob(h) for st, h in sh.items()}
    print('snapped', p, 'stages', sorted(snaps[p]))

# ---------- helpers ----------
def jload(p, st):
    return json.loads(snaps[p][st].decode('utf-8'))

TS_RE = re.compile(r'^20\d{2}-')
def deep_ts(obj, path=''):
    """hardened probe r100/R350: normalize key strip [_/-] before stem match;
    values must be ^20\\d{2}- AND contain time-of-day to feed wall-clock max."""
    best = None
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = re.sub(r'[_\-/]', '', str(k)).lower()
            if isinstance(v, str) and TS_RE.match(v) and re.search(r'[T ]\d{2}:\d{2}', v):
                if nk.startswith(('asof', 'updated', 'generated', 'lastattempt', 'lastfetch', 'ts', 'datetime', 'written')):
                    if best is None or v > best[0]:
                        best = (v, path + '/' + str(k))
            sub = deep_ts(v, path + '/' + str(k))
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:200]):
            sub = deep_ts(v, f'{path}[{i}]')
            if sub and (best is None or sub[0] > best[0]):
                best = sub
    return best

def take_new(p):
    a = deep_ts(jload(p, 2)); b = deep_ts(jload(p, 3))
    print(f'  probe {p}: HEAD {a} | MINE {b}')
    if a and b:
        side = 2 if a[0] >= b[0] else 3
    elif a: side = 2
    elif b: side = 3
    else: side = 2
    print(f'  -> take side {side}')
    return snaps[p][side]

resolved = {}

# ---------- 1) snapshot family x10 ----------
for p in ('results/dashboard_status.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/heat_update_status.json',
          'results/lhb_update_status.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/token_usage.json',
          'results/update_status.json', 'results/prospect_promotion/_summary.json'):
    if p in stages:
        resolved[p] = take_new(p)

# daily_report twins: same-side (probe json twin)
paj = 'docs/daily_report/REPORT-2026-09-28.json'
a = deep_ts(jload(paj, 2)); b = deep_ts(jload(paj, 3))
side = 2 if (a and (not b or a[0] >= b[0])) else 3
print(f'daily_report probe: HEAD {a} | MINE {b} -> side {side}')
for p in (paj, 'docs/daily_report/REPORT-2026-09-28.md'):
    resolved[p] = snaps[p][side]

# dashboard_status.js: whole-side bytes by inner ts
p = 'results/dashboard_status.js'
def js_ts(data):
    m = re.search(r'window\.DASH_DATA\s*=\s*(\{.*\})\s*;?', data.decode('utf-8'), re.S)
    return deep_ts(json.loads(m.group(1))) if m else None
a, b = js_ts(snaps[p][2]), js_ts(snaps[p][3])
side = 2 if (a and (not b or a[0] >= b[0])) else 3
print(f'dashboard.js probe: HEAD {a} | MINE {b} -> side {side}')
resolved[p] = snaps[p][side]

# ---------- 2) ledger unions ----------
def union_by(rows, keyf):
    seen, out = set(), []
    for r in rows:
        k = keyf(r)
        if k in seen: continue
        seen.add(k); out.append(r)
    return out

# compute_audit: history union + state take-new
p = 'results/compute_audit.json'
A, B = jload(p, 2), jload(p, 3)
hist_key = next((k for k in A if k in ('history', 'samples', 'runs', 'audit_history')), None)
if hist_key:
    na, nb = len(A.get(hist_key, [])), len(B.get(hist_key, []))
    merged_rows = union_by(list(A.get(hist_key, [])) + list(B.get(hist_key, [])),
                           lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
    merged_rows.sort(key=lambda r: (deep_ts(r) or ('', ''))[0])
    base = A if (deep_ts(A) or ('',))[0] >= (deep_ts(B) or ('',))[0] else B
    M = dict(base); M[hist_key] = merged_rows
    print(f'compute_audit: {hist_key} union {na}+{nb}->{len(merged_rows)} (|A∪B| check: {na}+{nb}-{len(merged_rows)} dup absorbed)')
else:
    M = json.loads(take_new(p).decode('utf-8'))
resolved[p] = json.dumps(M, ensure_ascii=False, indent=1).encode('utf-8')

# regime_state: transitions/history union + state take-new
p = 'results/regime_state.json'
A, B = jload(p, 2), jload(p, 3)
M = dict(A if (deep_ts(A) or ('',))[0] >= (deep_ts(B) or ('',))[0] else B)
for k in ('transitions', 'history'):
    if k in A or k in B:
        ra, rb = A.get(k, []), B.get(k, [])
        rows = union_by(list(ra) + list(rb), lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
        rows.sort(key=lambda r: (deep_ts(r) or (r.get('date', ''), ''))[0] if isinstance(r, dict) else str(r))
        M[k] = rows
        print(f'regime_state: {k} union {len(ra)}+{len(rb)}->{len(rows)}')
resolved[p] = json.dumps(M, ensure_ascii=False, indent=1).encode('utf-8')

# ---------- 3) CODELY.md: merge-base direct-concat (D-20260927-09) ----------
p = 'CODELY.md'
assert 1 in snaps[p], 'merge-base stage missing for CODELY.md'
base_b = snaps[p][1].decode('utf-8')
head = snaps[p][2].decode('utf-8')
mine = snaps[p][3].decode('utf-8')
assert head.startswith(base_b), 'prefix-identity FAIL on HEAD side (in-place edit? manual review)'
assert mine.startswith(base_b), 'prefix-identity FAIL on MINE side (in-place edit? manual review)'
head_suf = head[len(base_b):]
mine_suf = mine[len(base_b):]
merged = base_b + head_suf + (('\n' if head_suf and not head_suf.endswith('\n') else '') + mine_suf if mine_suf else '')
if not merged.endswith('\n'):
    merged += '\n'
resolved[p] = merged.encode('utf-8')
print(f'CODELY direct-concat: base {len(base_b)}B + HEAD-suffix {len(head_suf)}B + MINE-suffix {len(mine_suf)}B = {len(resolved[p])}B (zero loss, verbatim, no dedupe)')

# ---------- 4) write-back + parse-verify + add ----------
for p, data in resolved.items():
    if p.endswith('.json'):
        json.loads(data.decode('utf-8'))  # parse-verify before write
    with open(p, 'wb') as f:
        f.write(data)
for p in resolved:
    run(['git', 'add', p], check=False)
r = run(['git', 'status', '--porcelain'])
uu_left = [l for l in r.stdout.decode('utf-8').splitlines() if l.startswith('UU') or l.startswith('AA')]
print('post-add UU/AA remaining:', uu_left if uu_left else 'NONE')

sz = os.path.getsize('CODELY.md')
print('CODELY.md final size:', sz)
if sz > 10240:
    print('WARN: over 10,240B hard line -- same-window hot/cold fold needed')

rc = run(['git', '-c', 'core.editor=true', 'rebase', '--continue'])
print('rebase --continue rc=', rc.returncode)
print(rc.stdout.decode('utf-8', 'replace')[-300:])
print(rc.stderr.decode('utf-8', 'replace')[-200:])
if rc.returncode == 0:
    pr = run(['git', 'push'])
    print('push rc=', pr.returncode)
    print(pr.stderr.decode('utf-8', 'replace')[-200:])
sys.exit(rc.returncode)
