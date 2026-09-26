# -*- coding: utf-8 -*-
# r277 bm-b rebase resolver: 14-UU same-window S6 product family vs bm-a r275 (960d7a45).
# Sides in rebase: :2 = ours = origin/new base (bm-a face); :3 = theirs = my replayed commit.
# Recipes per classify_conflicts.py output + SKILL.md:
#   snapshots: take-new whole bytes by recursive normalized ts probe (r267 recursive law,
#              r265 format-normalize law, r140 tie->HEAD)
#   same-producer twins: json governs, md/js same side whole bytes (r265 pairing law)
#   rolling-ledger (compute_audit history / regime history+transitions): union zero-loss
#              + snapshot fields take-new (r188/R208)
#   mixed-dict+ledger (autofill): launches union cap50 ts-asc write-back (r245),
#              last_tick inner-ts newer, tie->HEAD, isinstance dict assert (r215/r140)
#   daily_scorecard (no ts face): parse-equality check -> whole bytes; else deep probe.
import json, subprocess, sys

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True)
    if r.returncode != 0:
        print('FATAL: cannot read', stage, path)
        sys.exit(2)
    return r.stdout

def norm_ts(v):
    return v.replace('T', ' ').replace('+08:00', '').strip()

def flat_ts(obj):
    out = []
    stack = [obj]
    while stack:
        v = stack.pop()
        if isinstance(v, dict):
            stack.extend(v.values())
        elif isinstance(v, list):
            stack.extend(v)
        elif isinstance(v, str) and len(v) >= 10 and v[:2] == '20' and ('-' in v[:5]):
            out.append(norm_ts(v))
    return out

def side_by_ts(path):
    """Return 2 or 3 by max normalized ts; tie -> 2 (HEAD, r140)."""
    a, b = json.loads(blob(2, path).decode('utf-8-sig')), json.loads(blob(3, path).decode('utf-8-sig'))
    ma, mb = max(flat_ts(a), default=''), max(flat_ts(b), default='')
    side = 3 if mb > ma else 2
    print(f'{path}: ts {ma} vs {mb} -> side {side} ({"mine" if side==3 else "origin/tie"})')
    return side

def take_whole(path, side):
    open(path, 'wb').write(blob(side, path))

def ident(o):
    return json.dumps(o, sort_keys=True, ensure_ascii=False)

# ---------- same-producer twin pairs (json governs) ----------
rep_side = side_by_ts('docs/daily_report/REPORT-2026-09-26.json')
take_whole('docs/daily_report/REPORT-2026-09-26.json', rep_side)
take_whole('docs/daily_report/REPORT-2026-09-26.md', rep_side)

dash_side = side_by_ts('results/dashboard_status.json')
take_whole('results/dashboard_status.json', dash_side)
take_whole('results/dashboard_status.js', dash_side)   # R209: whole bytes, wrapper intact

# ---------- plain snapshots: take-new whole bytes ----------
for p in ['results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
          'results/heat_update_status.json', 'results/lhb_update_status.json',
          'results/scorecard_v1.json', 'results/strategy_scorecard.json',
          'results/token_usage.json', 'results/update_status.json']:
    take_whole(p, side_by_ts(p))

# ---------- daily_scorecard.json (no top ts face): parse-equality gate ----------
p = 'results/daily_scorecard.json'
a, b = json.loads(blob(2, p).decode('utf-8-sig')), json.loads(blob(3, p).decode('utf-8-sig'))
if ident(a) == ident(b):
    print(f'{p}: both sides parse-equal -> take :3 bytes')
    take_whole(p, 3)
else:
    ma, mb = max(flat_ts(a), default=''), max(flat_ts(b), default='')
    side = 3 if mb > ma else 2
    print(f'{p}: UNEQUAL (deep-list ts {ma} vs {mb}) -> side {side}')
    take_whole(p, side)

# ---------- rolling-ledger unions ----------
def union_ledger(path, ledger_keys, ts_key='ts'):
    a, b = json.loads(blob(2, path).decode('utf-8-sig')), json.loads(blob(3, path).decode('utf-8-sig'))
    out = dict(b)  # newer snapshot face carries state fields (probe showed :3 newer)
    for k in ledger_keys:
        la, lb = a.get(k) or [], b.get(k) or []
        seen = {}
        for row in la + lb:
            seen[ident(row)] = row
        merged = sorted(seen.values(), key=lambda r: str(r.get(ts_key, '')))
        out[k] = merged
        print(f'{path}: {k} union {len(la)}+{len(lb)} -> {len(merged)} (|A u B|={len(seen)})')
    raw1 = blob(1, path)
    bom = raw1.startswith(b'\xef\xbb\xbf')
    crlf = b'\r\n' in raw1
    nl = raw1.endswith(b'\n')
    indent = 2 if b'\n  "' in raw1[:400] else 1
    data = json.dumps(out, ensure_ascii=False, indent=indent).encode('utf-8-sig' if bom else 'utf-8')
    if crlf:
        data = data.replace(b'\n', b'\r\n')
    if nl and not data.endswith(b'\r\n' if crlf else b'\n'):
        data += b'\r\n' if crlf else b'\n'
    open(path, 'wb').write(data)
    back = json.loads(open(path, 'rb').read().decode('utf-8-sig'))
    for k in ledger_keys:
        assert len(back[k]) >= len(out[k]), f'{k} row loss'

union_ledger('results/compute_audit.json', ['history'])
union_ledger('results/regime_state.json', ['history', 'transitions'])

# ---------- autofill_state (mixed-dict+ledger, r203/R208/r215/r220/r245) ----------
p = 'results/autofill_state.json'
ja, jb = json.loads(blob(2, p).decode('utf-8-sig')), json.loads(blob(3, p).decode('utf-8-sig'))
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
print(f'{p}: union {len(ja["launches"])}+{len(jb["launches"])} -> {len(out["launches"])}; last_tick {ta} vs {tb} -> {out["last_tick"].get("ts")} ({"mine" if tb>ta else "origin/tie"})')
raw1 = blob(1, p)
bom = raw1.startswith(b'\xef\xbb\xbf')
crlf = b'\r\n' in raw1
nl = raw1.endswith(b'\n')
indent = 2 if b'\n  "' in raw1[:400] else 1
data = json.dumps(out, ensure_ascii=False, indent=indent).encode('utf-8-sig' if bom else 'utf-8')
if crlf:
    data = data.replace(b'\n', b'\r\n')
if nl and not data.endswith(b'\r\n' if crlf else b'\n'):
    data += b'\r\n' if crlf else b'\n'
open(p, 'wb').write(data)
back = json.loads(open(p, 'rb').read().decode('utf-8-sig'))
assert isinstance(back['last_tick'], dict)
assert len(back['launches']) == len(out['launches'])

# ---------- parse-verify every resolved file ----------
resolved = ['docs/daily_report/REPORT-2026-09-26.json', 'docs/daily_report/REPORT-2026-09-26.md',
            'results/daily_scorecard.json', 'results/dashboard_status.json', 'results/dashboard_status.js',
            'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
            'results/heat_update_status.json', 'results/lhb_update_status.json',
            'results/regime_state.json', 'results/scorecard_v1.json', 'results/strategy_scorecard.json',
            'results/token_usage.json', 'results/update_status.json',
            'results/compute_audit.json', 'results/autofill_state.json']
for p in resolved:
    if p.endswith('.js'):
        raw = open(p, 'rb').read()
        assert b'window.DASH_DATA' in raw and raw.rstrip().endswith(b';'), f'{p} wrapper broken'
    elif p.endswith('.md'):
        open(p, encoding='utf-8').read()
    else:
        json.loads(open(p, 'rb').read().decode('utf-8-sig'))
print('ALL %d RESOLVED FILES PARSE-VERIFIED' % len(resolved))
