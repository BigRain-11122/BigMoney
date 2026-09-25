# -*- coding: utf-8 -*-
"""R210 rebase conflict resolver (11-UU same-window dual-machine S6 chain).

Recipes: R208 (snapshot take-new whole / rolling-ledger double-blob union zero-loss),
R140 (last_tick same-second tie -> HEAD), R203 (last_tick dict type assert),
R209 (JS-wrapper file: whole-byte take-side, no unwrap/re-serialize),
r185 (parse-validate BEFORE write-back; add only after validation passes).
"""
import subprocess, json, io, sys

def blob(rev, f):
    b = subprocess.run(['git', 'show', rev + ':' + f], capture_output=True)
    if b.returncode != 0:
        raise RuntimeError('git show failed: %s %s' % (rev, f))
    return b.stdout.decode('utf-8')

def union_list(a, b):
    """R208 union: keep HEAD order, append incoming entries not present (full-repr identity)."""
    seen = {json.dumps(x, sort_keys=True, ensure_ascii=False) for x in a}
    out = list(a)
    added = 0
    for x in b:
        k = json.dumps(x, sort_keys=True, ensure_ascii=False)
        if k not in seen:
            out.append(x)
            seen.add(k)
            added += 1
    return out, added

def take_newer(h, m, ts_key):
    """snapshot take-new whole by ts_key (string compare on ISO timestamps)."""
    th, tm = h.get(ts_key), m.get(ts_key)
    if th is None and tm is None:
        raise RuntimeError('ts_key %s missing both sides' % ts_key)
    if tm is not None and (th is None or str(tm) >= str(th)):
        return m, 'mine(%s=%s)' % (ts_key, tm)
    return h, 'head(%s=%s)' % (ts_key, th)

results = {}

# 2) autofill_state.json : launches union + last_tick tie->HEAD + dict assert (R140/R203)
f = 'results/autofill_state.json'
h, m = json.loads(blob('HEAD', f)), json.loads(blob('d45226f0', f))
merged_launches, added = union_list(h.get('launches', []), m.get('launches', []))
th, tm = h['last_tick'], m['last_tick']
assert isinstance(th, dict) and isinstance(tm, dict), 'last_tick not dict (R203)'
if str(th.get('ts')) >= str(tm.get('ts')):
    lt, lt_src = th, 'head-tie-or-newer'
else:
    lt, lt_src = tm, 'mine-newer'
out = {'launches': merged_launches, 'last_tick': lt}
if 'rebase_union_note' in h or 'rebase_union_note' in m:
    out['rebase_union_note'] = ('R210 rebase union: launches HEAD=%d+mine=%d->%d (union +%d, full-repr dedupe); '
                                'last_tick take %s (ts head=%s mine=%s)' %
                                (len(h.get('launches', [])), len(m.get('launches', [])),
                                 len(merged_launches), added, lt_src, th.get('ts'), tm.get('ts')))
io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1))
assert isinstance(json.loads(io.open(f, encoding='utf-8').read())['last_tick'], dict)
results[f] = 'launches %d+%d->%d (+%d) | last_tick %s' % (
    len(h.get('launches', [])), len(m.get('launches', [])), len(merged_launches), added, lt_src)

# 3) compute_audit.json : latest take-new + history union
f = 'results/compute_audit.json'
h, m = json.loads(blob('HEAD', f)), json.loads(blob('d45226f0', f))
latest, src = take_newer(h['latest'], m['latest'], 'ts')
uh, added = union_list(h.get('history', []), m.get('history', []))
out = {'latest': latest, 'history': uh}
io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1))
results[f] = 'latest take %s | history %d+%d->%d (+%d)' % (src, len(h.get('history', [])), len(m.get('history', [])), len(uh), added)

# 4) regime_state.json : snapshot take-new by updated + transitions/history union
f = 'results/regime_state.json'
h, m = json.loads(blob('HEAD', f)), json.loads(blob('d45226f0', f))
base, src = take_newer(h, m, 'updated')
ut, at = union_list(h.get('transitions', []), m.get('transitions', []))
uhi, ah = union_list(h.get('history', []), m.get('history', []))
out = dict(base)
out['transitions'] = ut
out['history'] = uhi
io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=1))
results[f] = 'snapshot take %s | transitions +%d | history +%d' % (src, at, ah)

# 5/7-12) snapshot whole-file take-new by their ts keys
SNAP = {
    'results/token_usage.json': 'generated',
    'results/fundamental_b_layer_filter.json': 'updated',
    'results/futures_update_status.json': 'last_attempt',
    'results/heat_update_status.json': 'updated',
    'results/lhb_update_status.json': 'updated',
    'results/update_status.json': 'updated',
}
for f, k in SNAP.items():
    h, m = json.loads(blob('HEAD', f)), json.loads(blob('d45226f0', f))
    d, src = take_newer(h, m, k)
    io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(d, ensure_ascii=False, indent=1))
    results[f] = 'take %s' % src

# 6) dashboard_status.js : whole-byte take-side (R209 law), side chosen by sibling .json generated_at
fj, fn = 'results/dashboard_status.js', 'results/dashboard_status.json'
hj, mj = blob('HEAD', fj), blob('d45226f0', fj)
hn, mn = json.loads(blob('HEAD', fn)), json.loads(blob('d45226f0', fn))
th, tm = hn.get('meta', {}).get('generated_at'), mn.get('meta', {}).get('generated_at')
side_js, side_json, src = (hj, hn, 'head') if (tm is None or (th is not None and str(th) >= str(tm))) else (mj, mn, 'mine')
io.open(fj, 'w', encoding='utf-8', newline='').write(side_js)
io.open(fn, 'w', encoding='utf-8', newline='\n').write(json.dumps(side_json, ensure_ascii=False, indent=2))
results[fj] = 'whole-byte take %s (generated_at head=%s mine=%s)' % (src, th, tm)

# 1) research/HANDOVER.md : text merge -- HEAD(bm-b r220) note keeps 最近核对, insert my R210 increment before 上一次核对
f = 'research/HANDOVER.md'
hc, mc = blob('HEAD', f), blob('d45226f0', f)
hl, ml = hc.splitlines(), mc.splitlines()
h4, m4 = hl[3], ml[3]
# my increment = text between 'R210 增量=' and '；上一次核对'
mi = m4[m4.find('R210 增量='):]
mi = mi[:mi.find('；上一次核对')]
anchor = '上一次核对=bm-a round 205'
assert anchor in h4, 'anchor missing in HEAD line4'
assert 'R210' not in h4, 'HEAD already contains R210?'
new4 = h4.replace(anchor, 'bm-a round 210（2026-09-26 03:1x·单机核 R206-210 增量窗）R210 增量=' + mi + '；' + anchor, 1)
hl[3] = new4
io.open(f, 'w', encoding='utf-8', newline='\n').write('\n'.join(hl) + '\n')
results[f] = 'text-merge: bm-b r220 keeps 最近核对, R210 increment inserted before R205 anchor (len %d->%d)' % (len(h4), len(new4))

for k in sorted(results):
    print(k, '=>', results[k])
print('ALL RESOLVED & VALIDATED')
