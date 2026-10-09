# -*- coding: utf-8 -*-
# r918 bm-a rebase UU resolver (3 faces, r907/r910 canon): attrition snapshot
# take-newer (stage3 mine 15:07:31 > stage2 15:06:51), token_usage take-newer
# (stage3 mine 15:07:12 > 14:47:37, per-machine sections identical), compute_audit
# rolling-history full-json dedupe UNION zero-loss (206+201 -> 207, latest=mine).
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def show(stage, path):
    return subprocess.run(['git', 'show', f':{stage}:{path}'], capture_output=True).stdout

# 1. attrition snapshot: take stage3 (mine, newer ts) -- raw bytes verbatim
mine_attr = show(3, 'results/_attrition_guard_scan.json')
theirs_attr = show(2, 'results/_attrition_guard_scan.json')
ma = json.loads(mine_attr.decode('utf-8')); ta = json.loads(theirs_attr.decode('utf-8'))
assert ma['ts'] > ta['ts'], f"attrition ts not newer: {ma['ts']} vs {ta['ts']}"
assert ma.get('rc') == 0 and ma.get('active_loss') is False, "mine attrition not CLEAN"
open('results/_attrition_guard_scan.json', 'wb').write(mine_attr)
print('attrition: take stage3 mine ts', ma['ts'], '(theirs', ta['ts'], ') rc', ma['rc'], 'active_loss', ma['active_loss'])

# 2. token_usage: take stage3 (mine, newer generated; sections identical)
mine_tk = show(3, 'results/token_usage.json')
theirs_tk = show(2, 'results/token_usage.json')
mt = json.loads(mine_tk.decode('utf-8')); tt = json.loads(theirs_tk.decode('utf-8'))
assert mt['generated'] > tt['generated'], f"token generated not newer: {mt['generated']} vs {tt['generated']}"
assert mt['machines'] == tt['machines'], "per-machine sections NOT identical -- abort take-newer"
open('results/token_usage.json', 'wb').write(mine_tk)
print('token_usage: take stage3 mine generated', mt['generated'], '(theirs', tt['generated'], ') sections identical 5/5')

# 3. compute_audit: rolling-history full-json dedupe UNION, sorted by ts, latest=mine
ca = json.loads(show(2, 'results/compute_audit.json').decode('utf-8'))
cb = json.loads(show(3, 'results/compute_audit.json').decode('utf-8'))
seen = {}
order = []
for h in ca['history'] + cb['history']:
    k = json.dumps(h, sort_keys=True, ensure_ascii=False)
    if k not in seen:
        seen[k] = h
        order.append(k)
hist = sorted(seen.values(), key=lambda h: h.get('ts', ''))
ka = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in ca['history']}
kb = {json.dumps(h, sort_keys=True, ensure_ascii=False) for h in cb['history']}
assert ka | kb <= set(order), "compute_audit union zero-loss assert failed"
out = {'history': hist, 'latest': cb['latest']}
raw_probe = show(3, 'results/compute_audit.json')
indent = 1 if b'\n "' in raw_probe or b'\n  "' in raw_probe[:2000] else None
open('results/compute_audit.json', 'w', encoding='utf-8', newline='').write(
    json.dumps(out, ensure_ascii=False, indent=1))
print('compute_audit: union', len(ca['history']), '+', len(cb['history']),
      '->', len(hist), '(origin-only', len(ka - kb), 'mine-only', len(kb - ka),
      ') latest=mine ts', cb['latest'].get('ts'))
print('RESOLVED 3/3 faces, zero-loss asserts PASS')
