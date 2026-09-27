# -*- coding: utf-8 -*-
"""r346 bm-b storm resolver (r355 family canon, single-process atomic):
1) snapshot all UU stage blobs up-front (tick-race minimization, r335/r351 awareness)
2) per-file recipe routing (classifier output):
   - snapshot family: hardened deep-ts probe on STAGED blobs, take-new whole side
   - daily_report twins: same-side take-new
   - dashboard_status.js: whole-side bytes
   - compute_audit / regime_state: ledger union + take-new state
   - autofill_state: launches union cap50 asc + last_tick max-ts whole-dict
   - CODELY.md: origin side as base + my r346 pointer appended (batch -> 34th, r176 yield)
   - memory-archive: origin content + my section renumbered to 34th batch
3) parse-verify every JSON before write-back; add all; rebase --continue; push.
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

def jloadb(p, st):
    return json.loads(snaps[p][st].decode('utf-8'))

TS_RE = re.compile(r'^20\d{2}-')
def deep_ts(obj, acc=None, path=''):
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

def take_new(p, prefer_head_on_tie=True):
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

# ---------- 1) snapshot family ----------
for p in ('results/dashboard_status.json', 'results/fundamental_b_layer_filter.json',
          'results/futures_update_status.json', 'results/heat_update_status.json',
          'results/lhb_update_status.json', 'results/prospect_promotion/_summary.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/token_usage.json', 'results/update_status.json'):
    resolved[p] = take_new(p)

# daily_report twins: same-side (probe json twin)
paj = 'docs/daily_report/REPORT-2026-09-27.json'
a = deep_ts(jload(paj, 2)); b = deep_ts(jload(paj, 3))
side = 2 if (a and (not b or a[0] >= b[0])) else 3
print(f'daily_report probe: HEAD {a} | MINE {b} -> side {side}')
for p in (paj, 'docs/daily_report/REPORT-2026-09-27.md'):
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
    merged_rows = union_by(list(A.get(hist_key, [])) + list(B.get(hist_key, [])),
                           lambda r: json.dumps(r, sort_keys=True, ensure_ascii=False))
    merged_rows.sort(key=lambda r: (deep_ts(r) or ('', ''))[0])
    base = A if (deep_ts(A) or ('',))[0] >= (deep_ts(B) or ('',))[0] else B
    M = dict(base); M[hist_key] = merged_rows
    print(f'compute_audit: {hist_key} union {len(A.get(hist_key, []))}+{len(B.get(hist_key, []))}->{len(merged_rows)}')
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

# autofill_state: launches union cap50 asc + last_tick whole-dict max-ts
p = 'results/autofill_state.json'
A, B = jload(p, 2), jload(p, 3)
la, lb = A.get('launches', []), B.get('launches', [])
rows = union_by(list(la) + list(lb), lambda r: (r.get('ts'), r.get('machine'), r.get('entry'), r.get('shard'), r.get('pid')))
rows.sort(key=lambda r: (r.get('ts') or '', r.get('machine') or ''))
rows = rows[-50:]  # keep newest 50 (cap semantics R215)
rows.sort(key=lambda r: (r.get('ts') or '', r.get('machine') or ''))  # re-sort asc for write-back (r245)
ta = A.get('last_tick', {}).get('ts', ''); tb = B.get('last_tick', {}).get('ts', '')
M = dict(A if ta >= tb else B)
M['launches'] = rows
assert isinstance(M.get('last_tick'), dict), 'last_tick must stay dict'
crlf = b'\r\n' in snaps[p][2][:2000]
print(f'autofill_state: launches {len(la)}+{len(lb)}->cap{len(rows)} last_tick winner ts={max(ta, tb)} crlf={crlf}')
txt = json.dumps(M, ensure_ascii=False, indent=1)
resolved[p] = (txt.replace('\n', '\r\n') if crlf else txt).encode('utf-8')

# ---------- 3) CODELY.md: origin base + my r346 pointer (batch renumbered 33->34) ----------
p = 'CODELY.md'
head = snaps[p][2].decode('utf-8'); mine = snaps[p][3].decode('utf-8')
# my new line = the one containing 'r346 bm-b' (pointer form), not present in head
my_lines = [l for l in mine.split('\n') if 'r346 bm-b' in l and l.startswith('- [')]
print('my r346 lines on mine-side:', len(my_lines))
add = [l.replace('\u4e09\u5341\u4e09\u6279', '\u4e09\u5341\u56db\u6279') for l in my_lines]
base = head.rstrip('\n')
merged_codely = base + '\n' + '\n'.join(add) + '\n'
resolved[p] = merged_codely.encode('utf-8')
print('CODELY merged bytes:', len(resolved[p]))

# ---------- 4) archive: origin content + my section renumbered to 34th ----------
p = 'research/memory-archive/202609.md'
head = snaps[p][2].decode('utf-8'); mine = snaps[p][3].decode('utf-8')
hl, ml = head.split('\n'), mine.split('\n')
i = 0
while i < min(len(hl), len(ml)) and hl[i] == ml[i]: i += 1
my_suffix = ml[i:]  # my new section (33rd batch -> renumber 34th)
renamed = ('\n'.join(my_suffix)).replace('\u4e09\u5341\u4e09\u6279', '\u4e09\u5341\u56db\u6279')
merged_arch = head.rstrip('\n') + '\n' + renamed.lstrip('\n')
if not merged_arch.endswith('\n'): merged_arch += '\n'
resolved[p] = merged_arch.encode('utf-8')
print('archive merged bytes:', len(resolved[p]), '| my suffix lines:', len(my_suffix))

# ---------- 5) write-back + parse-verify + add ----------
for p, data in resolved.items():
    if p.endswith('.json'):
        json.loads(data.decode('utf-8'))  # parse-verify before write
    with open(p, 'wb') as f:
        f.write(data)
for p in resolved:
    run(['git', 'add', p], check=False)
r = run(['git', 'status', '--porcelain'])
print('post-add status UU remaining:', [l for l in r.stdout.decode('utf-8').splitlines() if l.startswith('UU')])

# CODELY size check vs 10,000B hard line
sz = os.path.getsize('CODELY.md')
print('CODELY.md final size:', sz)
if sz > 10000:
    print('WARN: over 10,000B hard line -- follow-up fold needed this window')

rc = run(['git', '-c', 'core.editor=true', 'rebase', '--continue'])
print('rebase --continue rc=', rc.returncode)
print(rc.stdout.decode('utf-8', 'replace')[-400:])
print(rc.stderr.decode('utf-8', 'replace')[-300:])
if rc.returncode == 0:
    pr = run(['git', 'push'])
    print('push rc=', pr.returncode)
    print(pr.stdout.decode('utf-8', 'replace')[-200:])
    print(pr.stderr.decode('utf-8', 'replace')[-200:])
sys.exit(rc.returncode)
