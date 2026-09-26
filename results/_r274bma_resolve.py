# -*- coding: utf-8 -*-
"""R274 bm-a rebase-collision resolver (15 UU vs bm-b r275/r276 same-window push).
Recipes per bigmoney-conflict-resolve skill:
- CODELY.md memory-union (R208/r212): both machines' new entries kept, ts order (mine 22:40 < bm-b 22:48 -> mine first)
- compute_audit.json rolling-ledger (r188/R208): history union zero-loss, latest take-new (mine 22:41:07 > bm-b 22:36:37)
- regime_state.json rolling-ledger: history/transitions union, state fields take-new (mine 22:41:21 newer)
- snapshots take-new by ts (R208/R216): all bm-a-side newer (22:41-42 vs 22:36-37)
- dashboard_status.js js-wrapper (R209): take-side whole bytes (mine 22:42 build > bm-b 22:37), NO json re-dump
- REPORT-20260926.json/md r242 json-twin: json take-new (mine 22:42:17), md same-side whole bytes
- lhb_update_status.json co-written two faces: key-wise union {**ours,**theirs} zero-loss (bm-b 'overlap' key preserved)
"""
import subprocess, json

def blob(stage, p):
    r = subprocess.run(['git', 'show', f':{stage}:{p}'], capture_output=True)
    return r.stdout

def write(p, data: bytes):
    open(p, 'wb').write(data)

report = []

# ---- 1. CODELY.md memory-union ----
o = blob(2, 'CODELY.md').decode('utf-8')
t = blob(3, 'CODELY.md').decode('utf-8')
ol, tl = o.splitlines(), t.splitlines()
ours_only = [l for l in ol if l not in set(tl)]
theirs_only = [l for l in tl if l not in set(ol)]
# trunk = shared lines; then ours-only entries then theirs-only entries in ts order
trunk = [l for l in ol if l in set(tl)]
# append-order union: shared trunk + both sides' new lines, ours(bm-b 22:48) is LAST in HEAD;
# chronological: bm-a 22:40 first, bm-b 22:48 second
merged_lines = trunk + theirs_only + ours_only
# dedupe consecutive empties introduced by set-based trunk rebuild
out_txt = '\n'.join(merged_lines) + '\n'
write('CODELY.md', out_txt.encode('utf-8'))
json_ok = True  # md file, no parse gate
report.append(('CODELY.md', f'memory-union: trunk={len(trunk)} + bm-a-new={len(theirs_only)} + bm-b-new={len(ours_only)}'))

# ---- 2. compute_audit.json rolling-ledger ----
co = json.loads(blob(2, 'results/compute_audit.json').decode('utf-8'))
ct = json.loads(blob(3, 'results/compute_audit.json').decode('utf-8'))
ho, ht = co.get('history', []), ct.get('history', [])
seen, union = set(), []
for row in ho + ht:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); union.append(row)
# order union by row ts when present
def rts(r):
    return r.get('ts') or r.get('epoch') or ''
union.sort(key=lambda r: str(rts(r)))
merged = {'latest': ct['latest'], 'history': union}  # latest take-new (bm-a 22:41:07 newer)
# preserve any other top-level keys from the newer doc
for k, v in ct.items():
    if k not in merged: merged[k] = v
write('results/compute_audit.json', json.dumps(merged, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(('results/compute_audit.json', f'rolling-ledger union: hist |{len(ho)} u {len(ht)}|={len(union)}, latest=theirs(22:41:07)'))

# ---- 3. regime_state.json rolling-ledger ----
ro = json.loads(blob(2, 'results/regime_state.json').decode('utf-8'))
rt = json.loads(blob(3, 'results/regime_state.json').decode('utf-8'))
for key in ('history', 'transitions'):
    seen, union = set(), []
    for row in ro.get(key, []) + rt.get(key, []):
        k2 = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if k2 not in seen:
            seen.add(k2); union.append(row)
    rt[key] = union  # state fields take-new from theirs (bm-a updated 22:41:21)
write('results/regime_state.json', json.dumps(rt, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(('results/regime_state.json', f'rolling-ledger union hist={len(rt["history"])} trans={len(rt["transitions"])}, state=theirs(22:41:21)'))

# ---- 4. pure take-new snapshots (bm-a side newer) ----
for p in ['results/fundamental_b_layer_filter.json', 'results/token_usage.json',
          'results/update_status.json', 'results/heat_update_status.json',
          'results/futures_update_status.json', 'results/scorecard_v1.json',
          'results/strategy_scorecard.json', 'results/dashboard_status.json',
          'docs/daily_report/REPORT-2026-09-26.json']:
    b = blob(3, p)
    json.loads(b.decode('utf-8'))  # parse gate before write (r185)
    write(p, b)
    report.append((p, 'take-new theirs(bm-a 22:41-42)'))

# ---- 5. dashboard_status.js js-wrapper: take-side whole bytes ----
b = blob(3, 'results/dashboard_status.js')
assert b.startswith(b'window.') or b'DASH_DATA' in b[:200], 'js wrapper face lost'
write('results/dashboard_status.js', b)
report.append(('results/dashboard_status.js', 'js-wrapper take-side whole bytes theirs(22:42 build)'))

# ---- 6. REPORT md: json-twin same-side whole bytes ----
b = blob(3, 'docs/daily_report/REPORT-2026-09-26.md')
write('docs/daily_report/REPORT-2026-09-26.md', b)
report.append(('docs/daily_report/REPORT-2026-09-26.md', 'r242 json-twin: md same-side whole bytes'))

# ---- 7. lhb_update_status.json key-wise union (co-written, bm-b 'overlap' key preserved) ----
lo = json.loads(blob(2, 'results/lhb_update_status.json').decode('utf-8'))
lt = json.loads(blob(3, 'results/lhb_update_status.json').decode('utf-8'))
merged_l = {**lo, **lt}  # theirs newer ts overrides same keys; ours-only keys (overlap) preserved
merged_l['updated'] = lt.get('updated', lo.get('updated'))
write('results/lhb_update_status.json', json.dumps(merged_l, ensure_ascii=False, indent=1).encode('utf-8'))
report.append(('results/lhb_update_status.json', f'key-wise union: ours-only keys={sorted(set(lo)-set(lt))}, ts=theirs'))

for p, note in report:
    print(f'{p}: {note}')
print('resolver done, all parse-gated')
