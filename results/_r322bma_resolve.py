# -*- coding: utf-8 -*-
"""r322 bm-a S0 rebase-collision canon resolve (28 UU vs origin/main fbef43da).

Context: r321 push was rejected same-window vs bm-b r322 (12:34:29) + bm-c r80 (12:37:21);
backup branch machine/bm-a-r321 landed; this S0 rebase = the planned "main re-lands" step.
Three-machine same-window S6-mirror triple collision (r312/r320 precedent family).

Probe facts (_r322bma_probe.py -> _r322bma_probe_out.json):
  25 measurement-face files: pure runtime-ts diffs, origin side newer (12:33-12:34 vs ours 12:31-12:32)
    -> take origin (stage2) whole. Twins kept same-side (REPORT json+md, dashjs+json, export+latest).
  3 true ledgers -> union zero-loss:
    autofill_state.json  launches 57(origin) vs 50(r321); last_tick origin 12:30:02 > ours 12:30:01
    compute_audit.json   history 202(origin) vs 205(r321); latest origin 12:33:14 > ours 12:31:14
    x2_watch_log.jsonl   lines 648 vs 648 -> union 654 (6 only-each-side)

Laws applied: r317 (autofill key-level union (ts,machine,entry,shard,pid), whole-dict last_tick,
  indent/CRLF mirror), r188/R208 (ledger union), r140 (tie->HEAD), r319 (dedup key exists-in-entry +
  len==keyset-union assertion), r223/r245 (EOL mirror detect->write), r312 (facing-side done-absorb n/a),
  D-20260927-09 (deep ts probe), R209 (dashjs whole-bytes wrapper preserved).
Cap note: autofill launches cap-50 is owned by producer Tools/autofill.py L711 ([-50:] on append);
  resolver writes full zero-loss union (fleet practice r320bmb=55 / origin-r80=57 uncapped).
"""
import json, subprocess, sys

ROOT = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def blob(stage, path):
    r = subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        raise RuntimeError(f'blob miss :{stage}:{path}: {r.stderr[:200]}')
    return r.stdout

def detect_params(b):
    """find json.dumps params (+ newline style) that reproduce blob b byte-exactly."""
    obj = json.loads(b.decode('utf-8'))
    for indent in (1, 2, 4, None):
        for ea in (False, True):
            s = json.dumps(obj, indent=indent, ensure_ascii=ea)
            for nl, s2 in (('\r\n', s.replace('\n', '\r\n')), ('\n', s)):
                for tail in ('\n', ''):
                    if s2 + tail == b.decode('utf-8'):
                        return obj, indent, ea, nl, tail
    return obj, None, None, ('\r\n' if b'\r\n' in b[:2000] else '\n'), None

TAKE_ORIGIN = [
    'docs/daily_report/REPORT-2026-09-27.json', 'docs/daily_report/REPORT-2026-09-27.md',
    'results/daily_scorecard.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json', 'results/heat_update_status.json', 'results/lhb_update_status.json',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-24.json', 'results/paper_export/latest.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/t35_open_fill_verify.json', 'results/token_usage.json', 'results/update_status.json',
]

def launch_key(e):
    return (e.get('ts'), e.get('machine'), e.get('entry'), e.get('shard'), e.get('pid'))

log = {}

# ---------- 1. take-origin faces ----------
for p in TAKE_ORIGIN:
    b = blob(2, p)
    with open(p, 'wb') as f:
        f.write(b)
    if p.endswith('.json'):
        json.loads(open(p, 'rb').read().decode('utf-8-sig'))  # parse-verify
    elif p.endswith('.js'):
        head = b[:40]
        assert b.rstrip().endswith(b';') and b'window.DASH_DATA' in head, f'wrapper lost {p}'
    log[p] = f'take-origin ({len(b)}B)'

# ---------- 2. autofill_state.json (mixed-dict+ledger, r317) ----------
p = 'results/autofill_state.json'
b2, b3 = blob(2, p), blob(3, p)
o2, o3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
A = {launch_key(e): e for e in o2.get('launches', [])}   # origin/HEAD face
B = {launch_key(e): e for e in o3.get('launches', [])}   # r321 face
union = {**B, **A}                                        # HEAD(origin) preferred on key collision (r140)
merged = sorted(union.values(), key=lambda e: e.get('ts') or '')
assert len(merged) == len(set(A) | set(B)), f'zero-loss violated: {len(merged)} != {len(set(A)|set(B))}'
lt2, lt3 = o2.get('last_tick') or {}, o3.get('last_tick') or {}
last_tick = lt2 if str(lt2.get('ts', '')) >= str(lt3.get('ts', '')) else lt3   # inner-ts whole-dict (r317/r140)
assert isinstance(last_tick, dict), 'last_tick not dict'
out = {**o3, **o2}   # origin wins all top-level keys (newer state face)
out['launches'] = merged
out['last_tick'] = last_tick
_, indent, ea, nl, tail = detect_params(b2)
if indent is None: indent, ea, nl, tail = 1, False, '\r\n', '\r\n'   # r317 canon fallback
s = json.dumps(out, indent=indent, ensure_ascii=ea)
open(p, 'wb').write((s.replace('\n', nl) if nl == '\r\n' else s).encode('utf-8') + (tail.encode() if tail == '\n' else (b'\r\n' if nl == '\r\n' else b'')))
json.loads(open(p, 'rb').read().decode('utf-8'))
log[p] = f'launches union {len(A)}+{len(B)}->{len(merged)} zero-loss ts-asc, last_tick {"origin" if last_tick is lt2 else "r321"}@{last_tick.get("ts")}, indent={indent} nl={repr(nl)}'

# ---------- 3. compute_audit.json (rolling-ledger union, r188/r319) ----------
p = 'results/compute_audit.json'
b2, b3 = blob(2, p), blob(3, p)
o2, o3 = json.loads(b2.decode('utf-8')), json.loads(b3.decode('utf-8'))
hA, hB = o2.get('history', []), o3.get('history', [])
assert all('ts' in e for e in hA + hB), 'r319: history entries missing ts dedup key'
KA, KB = {e['ts']: e for e in hA}, {e['ts']: e for e in hB}
coll = sorted(set(KA) & set(KB))
union_h = {**KB, **KA}          # HEAD(origin) preferred on same-ts collision (r140)
merged_h = sorted(union_h.values(), key=lambda e: e['ts'])
assert len(merged_h) == len(set(KA) | set(KB)), 'zero-loss violated compute_audit'
out = {**o3, **o2}              # origin wins latest + all snapshot fields (ts 12:33:14 > 12:31:14)
out['history'] = merged_h
_, indent, ea, nl, tail = detect_params(b2)
if indent is None: indent, ea, nl, tail = 2, False, '\n', '\n'
s = json.dumps(out, indent=indent, ensure_ascii=ea)
data = (s.replace('\n', nl) if nl == '\r\n' else s).encode('utf-8') + (tail.encode() if tail else b'')
open(p, 'wb').write(data)
json.loads(open(p, 'rb').read().decode('utf-8'))
log[p] = f'history union {len(hA)}+{len(hB)}->{len(merged_h)} zero-loss ts-asc (same-ts collisions {len(coll)}), latest=origin@{out.get("latest",{}).get("ts")}, indent={indent}'

# ---------- 4. x2_watch_log.jsonl (append-log line union, r188) ----------
p = 'results/x2_watch_log.jsonl'
b2, b3 = blob(2, p), blob(3, p)
nl = '\r\n' if b2.count(b'\r\n') > b2.count(b'\n') - b2.count(b'\r\n') else '\n'
def lines_of(b):
    return [l for l in b.decode('utf-8').split('\r\n' if '\r\n' in b.decode('utf-8') else '\n') if l.strip()]
L2, L3 = lines_of(b2), lines_of(b3)
setU = sorted(set(L2) | set(L3))          # line-level union; sort = content-stable total order
assert len(setU) == len(set(L2) | set(L3))
for l in setU:
    json.loads(l)                          # every line valid json
out_b = (nl.join(setU) + nl).encode('utf-8')
open(p, 'wb').write(out_b)
log[p] = f'line union {len(L2)}+{len(L3)}->{len(setU)} zero-loss (only-origin {len(set(L2)-set(L3))}, only-r321 {len(set(L3)-set(L2))})'

# ---------- 5. stage resolved files ----------
resolved = TAKE_ORIGIN + ['results/autofill_state.json', 'results/compute_audit.json', 'results/x2_watch_log.jsonl']
assert len(resolved) == 28, f'expect 28, got {len(resolved)}'
for p in resolved:
    r = subprocess.run(['git', 'add', '--', p], capture_output=True, cwd=ROOT)
    assert r.returncode == 0, f'git add failed {p}: {r.stderr[:200]}'

with open('results/_r322bma_resolve_report.json', 'w', encoding='utf-8') as f:
    json.dump({'round': 'r322 bm-a S0 main-reland', 'origin_tip': 'fbef43da',
               'log': log, 'files_staged': len(resolved)}, f, ensure_ascii=False, indent=1)
print(json.dumps(log, ensure_ascii=False, indent=1))
print('STAGED', len(resolved), 'files; all parse-verified')
