# -*- coding: utf-8 -*-
# R277 bm-a rebase resolver: 18-UU same-window S6 product family + T-86 ticket vs bm-b r278/r279 face.
# Sides in rebase: :2 = ours = origin/new base (bm-b face); :3 = theirs = my replayed commit.
# Recipes per classify_conflicts.py + SKILL.md:
#   snapshots: take-new by DIFF-KEY ts probe (r267 recursive law; r265 format-normalize;
#              r277 constant-key exclusion via differencing; r140 tie->HEAD=:2)
#   same-producer twins: json governs, md/js same side whole bytes (r265 pairing law)
#   rolling-ledger (compute_audit history / regime history+transitions): union zero-loss
#              + snapshot fields take-new (r188/R208)
#   mixed-dict+ledger (autofill): launches union cap50 ts-asc write-back (r245),
#              last_tick inner-ts newer, tie->HEAD, isinstance dict assert (r215/r140)
#   append-log (post_review.jsonl): line-level union zero-loss (r188)
#   ticket field-merge (T-86): both sides' machine-tagged progress keys kept (r262 naming law)
import json, re, subprocess, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        print('FATAL: cannot read', stage, path); sys.exit(2)
    return r.stdout

def norm_ts(v):
    return v.replace('T', ' ').replace('+08:00', '').strip()

def flat(o, pre=''):
    out = {}
    if isinstance(o, dict):
        for k, v in o.items():
            out.update(flat(v, f'{pre}.{k}' if pre else str(k)))
    elif isinstance(o, list):
        for i, v in enumerate(o):
            out.update(flat(v, f'{pre}[{i}]'))
    else:
        out[pre] = o
    return out

def diff_ts_probe(path):
    """max normalized ts over keys where the two sides DIFFER (constant keys
    like paper.first_check cannot hijack -- r277 law); tie -> 2 (HEAD, r140)."""
    a = json.loads(blob(2, path).decode('utf-8-sig'))
    b = json.loads(blob(3, path).decode('utf-8-sig'))
    fa, fb = flat(a), flat(b)
    ma = mb = ''
    for k in set(fa) | set(fb):
        va, vb = fa.get(k), fb.get(k)
        if va == vb:
            continue
        for side, v in ((2, va), (3, vb)):
            if isinstance(v, str) and len(v) >= 10 and v[:2] == '20' and '-' in v[:5]:
                nv = norm_ts(v)
                if side == 2 and nv > ma: ma = nv
                if side == 3 and nv > mb: mb = nv
    side = 3 if mb > ma else 2
    print(f'{path}: diff-ts {ma} vs {mb} -> side {side} ({"mine" if side == 3 else "origin/tie"})')
    return side

def take_whole(path, side):
    open(path, 'wb').write(blob(side, path))

def ident(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)

def probe_face(raw):
    bom = raw.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw
    nl = raw.endswith(b'\n')
    indent = 2 if b'\n  "' in raw[:400] else 1
    return bom, crlf, nl, indent

def emit_json(path, obj, face_src):
    bom, crlf, nl, indent = probe_face(face_src)
    data = json.dumps(obj, ensure_ascii=False, indent=indent).encode('utf-8-sig' if bom else 'utf-8')
    if crlf:
        data = data.replace(b'\n', b'\r\n')
    if nl and not data.endswith(b'\r\n' if crlf else b'\n'):
        data += b'\r\n' if crlf else b'\n'
    open(path, 'wb').write(data)

# ---------- same-producer twin pairs (json governs) ----------
rep_side = diff_ts_probe('docs/daily_report/REPORT-2026-09-26.json')
take_whole('docs/daily_report/REPORT-2026-09-26.json', rep_side)
take_whole('docs/daily_report/REPORT-2026-09-26.md', rep_side)

dash_side = diff_ts_probe('results/dashboard_status.json')
take_whole('results/dashboard_status.json', dash_side)
take_whole('results/dashboard_status.js', dash_side)   # R209: whole bytes, wrapper intact

# ---------- plain snapshots: take-new ----------
for p in ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/token_usage.json', 'results/update_status.json']:
    take_whole(p, diff_ts_probe(p))

# ---------- rolling-ledger unions ----------
def union_ledger(path, ledger_keys, ts_key='ts'):
    a = json.loads(blob(2, path).decode('utf-8-sig'))
    b = json.loads(blob(3, path).decode('utf-8-sig'))
    newer = b if diff_ts_probe(path) == 3 else a
    out = dict(newer)   # snapshot/state fields take-new
    for k in ledger_keys:
        seen = {}
        for row in (a.get(k) or []) + (b.get(k) or []):
            seen[ident(row)] = row
        merged = sorted(seen.values(), key=lambda r: str(r.get(ts_key, '')))
        out[k] = merged
        print(f'{path}: {k} union {len(a.get(k) or [])}+{len(b.get(k) or [])} -> {len(merged)} (|A u B|={len(seen)})')
    emit_json(path, out, blob(1, path))
    back = json.loads(open(path, 'rb').read().decode('utf-8-sig'))
    for k in ledger_keys:
        assert len(back[k]) >= len(out[k]), f'{k} row loss'

union_ledger('results/compute_audit.json', ['history'])
union_ledger('results/regime_state.json', ['history', 'transitions'])

# ---------- autofill_state (mixed-dict+ledger) ----------
p = 'results/autofill_state.json'
ja = json.loads(blob(2, p).decode('utf-8-sig'))
jb = json.loads(blob(3, p).decode('utf-8-sig'))
out = dict(ja)
by_row = {}
for row in ja.get('launches', []) + jb.get('launches', []):
    by_row[ident(row)] = row
union_desc = sorted(by_row.values(), key=lambda r: r.get('ts', ''), reverse=True)
out['launches'] = sorted(union_desc[:50], key=lambda r: r.get('ts', ''))
ta = (ja.get('last_tick') or {}).get('ts')
tb = (jb.get('last_tick') or {}).get('ts')
out['last_tick'] = jb['last_tick'] if (tb and (not ta or tb > ta)) else ja['last_tick']
assert isinstance(out['last_tick'], dict), 'last_tick not dict'
print(f'{p}: launches union {len(ja.get("launches", []))}+{len(jb.get("launches", []))} '
      f'-> {len(out["launches"])}; last_tick {ta} vs {tb} -> {out["last_tick"].get("ts")}')
emit_json(p, out, blob(1, p))
back = json.loads(open(p, 'rb').read().decode('utf-8-sig'))
assert isinstance(back['last_tick'], dict)
assert len(back['launches']) == len(out['launches'])

# ---------- post_review.jsonl (append-log: line union zero-loss) ----------
p = 'results/post_review.jsonl'
la = blob(2, p).decode('utf-8', 'replace').splitlines()
lb = blob(3, p).decode('utf-8', 'replace').splitlines()
seen, order = set(), []
for ln in la + lb:
    if ln and ln not in seen:
        seen.add(ln); order.append(ln)
face = blob(1, p)
crlf = b'\r\n' in face
data = ('\r\n' if crlf else '\n').join(order)
if face.endswith(b'\n'):
    data += '\r\n' if crlf else '\n'
open(p, 'wb').write(data.encode('utf-8'))
print(f'{p}: line union {len(la)}+{len(lb)} -> {len(order)} (|A u B| zero-loss)')

# ---------- post_review/REPORT md (same-producer regen: bytes-equal or take-new) ----------
p = 'results/post_review/REPORT-20260926.md'
ra, rb = blob(2, p), blob(3, p)
if ra == rb:
    take_whole(p, 3)
    print(f'{p}: byte-identical sides -> :3')
else:
    def maxts(raw):
        return max((m.group(0) for m in re.finditer(rb'20\d{2}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}', raw)), default='')
    side = 3 if maxts(rb) > maxts(ra) else 2
    print(f'{p}: UNEQUAL ts {maxts(ra)} vs {maxts(rb)} -> side {side}')
    take_whole(p, side)

# ---------- T-86 ticket field-merge (machine-tagged progress keys both kept) ----------
p = 'fleet/tasks/T-2026-09-26-86-P1.json'
a = json.loads(blob(2, p).decode('utf-8-sig'))
b = json.loads(blob(3, p).decode('utf-8-sig'))
merged = dict(b)          # mine (progress_r277 + claim fields)
for k, v in a.items():
    if k not in merged:
        merged[k] = v      # bm-b's progress_r278_bmb preserved
emit_json(p, merged, blob(3, p))
back = json.loads(open(p, 'rb').read().decode('utf-8-sig'))
assert 'progress_r277' in back and 'progress_r278_bmb' in back and back.get('claimed_by') == 'bm-a'
print(f'{p}: merged keys progress_r277 + progress_r278_bmb (both machines preserved)')

# ---------- parse-verify everything ----------
resolved = ['docs/daily_report/REPORT-2026-09-26.json', 'docs/daily_report/REPORT-2026-09-26.md',
            'results/dashboard_status.json', 'results/dashboard_status.js',
            'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
            'results/heat_update_status.json', 'results/lhb_update_status.json',
            'results/scorecard_v1.json', 'results/strategy_scorecard.json',
            'results/token_usage.json', 'results/update_status.json',
            'results/compute_audit.json', 'results/regime_state.json',
            'results/autofill_state.json', 'results/post_review.jsonl',
            'results/post_review/REPORT-20260926.md', 'fleet/tasks/T-2026-09-26-86-P1.json']
for p in resolved:
    if p.endswith('.js'):
        raw = open(p, 'rb').read()
        assert b'window.DASH_DATA' in raw and raw.rstrip().endswith(b';'), f'{p} wrapper broken'
    elif p.endswith('.md'):
        open(p, encoding='utf-8').read()
    elif p.endswith('.jsonl'):
        for i, ln in enumerate(open(p, encoding='utf-8')):
            if ln.strip():
                json.loads(ln)
    else:
        json.loads(open(p, 'rb').read().decode('utf-8-sig'))
print(f'ALL {len(resolved)} RESOLVED FILES PARSE-VERIFIED')
