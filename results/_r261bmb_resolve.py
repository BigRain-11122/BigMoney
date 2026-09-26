# -*- coding: utf-8 -*-
# r261 S7 push-collision 13-UU resolver (rebase face: :2=origin/bm-a-r257 side, :3=bm-b r261 side)
# recipes per bigmoney-conflict-resolve skill: classify_conflicts output + r242/r257/r260 precedents
import subprocess, json, sys

def blob(rev, path):
    out = subprocess.run(['git', 'show', '%s:%s' % (rev, path)], capture_output=True)
    assert out.returncode == 0, (rev, path, out.stderr[:200])
    return out.stdout

def probe_ts(obj):
    # R242 law: probe candidate ts key family with real non-null values, never guess
    cands = []
    for k in ('generated_at', 'generated', 'updated', 'updated_at', 'ts', 'as_of', 'last_attempt', 'time', 'date'):
        v = obj.get(k) if isinstance(obj, dict) else None
        if v:
            cands.append((k, str(v)))
    return cands

FILES_SNAP = [
    'results/fundamental_b_layer_filter.json',
    'results/futures_update_status.json',
    'results/heat_update_status.json',
    'results/lhb_update_status.json',
    'results/token_usage.json',
    'results/update_status.json',
]
verdicts = []

# --- snapshots: take-new by probed ts; tie -> HEAD(origin) side per r140 ---
for p in FILES_SNAP:
    a = json.loads(blob(':2', p).decode('utf-8-sig'))   # origin side
    b = json.loads(blob(':3', p).decode('utf-8-sig'))   # mine r261
    ta, tb = probe_ts(a), probe_ts(b)
    ka = ta[0][1] if ta else None
    kb = tb[0][1] if tb else None
    if ka is None and kb is None:
        verdicts.append((p, 'UNKNOWN-no-ts', ka, kb)); continue
    side = 'theirs' if (kb is not None and (ka is None or kb > ka)) else 'ours'
    verdicts.append((p, 'take-' + side, ka, kb))
    raw = blob(':3' if side == 'theirs' else ':2', p)
    open(p, 'wb').write(raw)

# --- dashboard_status.json: nested meta.generated_at (probed r261) ---
p = 'results/dashboard_status.json'
a = json.loads(blob(':2', p).decode('utf-8-sig'))
b = json.loads(blob(':3', p).decode('utf-8-sig'))
ka = str((a.get('meta') or {}).get('generated_at') or '')
kb = str((b.get('meta') or {}).get('generated_at') or '')
side = 'theirs' if (kb and (not ka or kb > ka)) else 'ours'
verdicts.append((p, 'take-' + side + ' (meta.generated_at nested)', ka, kb))
open(p, 'wb').write(blob(':3' if side == 'theirs' else ':2', p))

# --- daily_scorecard.json: no ts in either blob; twin daily_scorecard.html auto-merged to mine
#     + my S6 chain ran fresher (16:47 vs bm-a 16:37 chain) -> twin-pair take mine whole ---
p = 'results/daily_scorecard.json'
verdicts.append((p, 'take-theirs (twin html auto-merged to mine + fresher run 16:47>16:37)', '-', 'r261 S6'))
open(p, 'wb').write(blob(':3', p))

# --- dashboard_status.js: js-wrapper-snapshot take-side whole bytes (probe generated_at inside wrapper) ---
pj = 'results/dashboard_status.js'
ja = blob(':2', pj).decode('utf-8-sig')
jb = blob(':3', pj).decode('utf-8-sig')
import re
def wrap_ts(s):
    m = re.search(r'"generated_at":\s*"([^"]+)"', s)
    return m.group(1) if m else None
tja, tjb = wrap_ts(ja), wrap_ts(jb)
side = 'theirs' if (tjb and (not tja or tjb > tja)) else 'ours'
verdicts.append((pj, 'take-' + side + ' whole-byte wrapper', tja, tjb))
open(pj, 'wb').write(blob(':3' if side == 'theirs' else ':2', pj))

# --- daily_report pair (r242 precedent): json twin generated_at decides, md same side whole-byte ---
pa, pm = 'docs/daily_report/REPORT-2026-09-26.json', 'docs/daily_report/REPORT-2026-09-26.md'
ja = json.loads(blob(':2', pa).decode('utf-8-sig'))
jb = json.loads(blob(':3', pa).decode('utf-8-sig'))
tja = ja.get('generated_at'); tjb = jb.get('generated_at')
side = 'theirs' if (tjb and (not tja or tjb > tja)) else 'ours'
verdicts.append((pa, 'pair-take-' + side + ' (r242: json generated_at governs, md same-side)', tja, tjb))
open(pa, 'wb').write(blob(':3' if side == 'theirs' else ':2', pa))
open(pm, 'wb').write(blob(':3' if side == 'theirs' else ':2', pm))

# --- rolling-ledger: compute_audit.json history union zero-loss + snapshot fields take-new ---
p = 'results/compute_audit.json'
a = json.loads(blob(':2', p).decode('utf-8-sig'))
b = json.loads(blob(':3', p).decode('utf-8-sig'))
ha = a.get('history', []); hb = b.get('history', [])
seen = set(); union = []
for row in ha + hb:
    key = json.dumps(row, sort_keys=True, ensure_ascii=False)
    if key not in seen:
        seen.add(key); union.append(row)
union.sort(key=lambda r: str(r.get('ts', '')))
merged = dict(b if str(b.get('ts', '')) >= str(a.get('ts', '')) else a)
merged['history'] = union
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(merged, ensure_ascii=False, indent=2) + '\n')
verdicts.append((p, 'history union %d|%d->%d zero-loss + state take-new' % (len(ha), len(hb), len(union)),
                 str(a.get('ts')), str(b.get('ts'))))

# --- rolling-ledger: regime_state.json transitions/history union dedupe + state take-new ---
p = 'results/regime_state.json'
a = json.loads(blob(':2', p).decode('utf-8-sig'))
b = json.loads(blob(':3', p).decode('utf-8-sig'))
def ukey(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)
merged = dict(b)
for arr_key in ('history', 'transitions', 'triggers'):
    va, vb = a.get(arr_key), b.get(arr_key)
    if isinstance(va, list) and isinstance(vb, list):
        seen = set(); un = []
        for row in va + vb:
            k = ukey(row)
            if k not in seen:
                seen.add(k); un.append(row)
        merged[arr_key] = un
        verdicts.append((p + '#' + arr_key, 'union %d|%d->%d' % (len(va), len(vb), len(un)), '-', '-'))
    elif va is not None and vb is None:
        merged[arr_key] = va
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(merged, ensure_ascii=False, indent=2) + '\n')

# --- parse-verify all resolved json files before staging (r185 law) ---
resolved = (FILES_SNAP + ['results/dashboard_status.json', 'results/daily_scorecard.json', pj, pa,
                          'results/compute_audit.json', 'results/regime_state.json'])
print('ALL RESOLVED, verifying parse...')
for path in resolved:
    if path.endswith('.json'):
        json.loads(open(path, encoding='utf-8-sig').read())
    elif path.endswith('.js'):
        s = open(path, encoding='utf-8-sig').read()
        m = re.search(r'window\.DASH_DATA\s*=\s*(\{.*\});', s, re.S)
        assert m, 'js wrapper lost in %s' % path
        json.loads(m.group(1))
print('ALL PARSE-VERIFIED')
for v in verdicts:
    print('|', v[0], '|', v[1], '| origin_ts:', v[2], '| mine_ts:', v[3])
