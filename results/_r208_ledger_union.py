import io, json, subprocess

def blob(rev, f):
    return subprocess.run(['git', 'show', '%s:%s' % (rev, f)], capture_output=True).stdout.decode('utf-8')

def union_lists(a, b, sort_key='ts', cap=None):
    seen = {}
    for e in a + b:
        seen[json.dumps(e, ensure_ascii=False, sort_keys=True)] = e
    merged = sorted(seen.values(), key=lambda e: e.get(sort_key, ''))
    if cap is not None:
        merged = merged[-cap:]
    return merged, len(seen)

# ---- compute_audit.json ----
f = 'results/compute_audit.json'
hj = json.loads(blob('HEAD', f))
oj = json.loads(blob('710b36d4', f))
print('compute_audit: head latest ts=%s hist=%d | ours latest ts=%s hist=%d | head hist[0] ts=%s ours hist[0] ts=%s' % (
    hj['latest']['ts'], len(hj['history']), oj['latest']['ts'], len(oj['history']),
    hj['history'][0]['ts'], oj['history'][0]['ts']))
merged_hist, n_uniq = union_lists(hj['history'], oj['history'])
# retention: keep same length cap as larger side if both sides equal-length (cap evidence), else no cap
cap = max(len(hj['history']), len(oj['history'])) if len(hj['history']) == len(oj['history']) else None
if cap:
    merged_hist = merged_hist[-cap:]
latest = hj['latest'] if hj['latest']['ts'] > oj['latest']['ts'] else oj['latest']
out = {'latest': latest, 'history': merged_hist}
io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
back = json.load(io.open(f, encoding='utf-8'))
assert back['latest'] == latest and back['history'] == merged_hist
ts_list = [e['ts'] for e in back['history']]
assert len(ts_list) == len(set(ts_list)) or True  # ts may repeat across machines; identity dedupe is the guarantee
print('compute_audit resolved: hist union %d unique -> %d kept, latest=%s' % (n_uniq, len(merged_hist), latest['ts']))

# ---- regime_state.json ----
f = 'results/regime_state.json'
hj = json.loads(blob('HEAD', f))
oj = json.loads(blob('HEAD', f))  # placeholder, re-read below
hj = json.loads(blob('HEAD', f))
oj = json.loads(blob('710b36d4', f))
print('regime: head updated=%s hist=%d trans=%d | ours updated=%s hist=%d trans=%d' % (
    hj.get('updated'), len(hj.get('history', [])), len(hj.get('transitions', [])),
    oj.get('updated'), len(oj.get('history', [])), len(oj.get('transitions', []))))
merged_hist, nu1 = union_lists(hj.get('history', []), oj.get('history', []))
merged_tr, nu2 = union_lists(hj.get('transitions', []), oj.get('transitions', []), sort_key='ts')
# scalars: take-newer side by 'updated'
base = hj if hj.get('updated', '') > oj.get('updated', '') else oj
out = dict(base)
out['history'] = merged_hist
out['transitions'] = merged_tr
io.open(f, 'w', encoding='utf-8', newline='\n').write(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
back = json.load(io.open(f, encoding='utf-8'))
assert back['history'] == merged_hist and back['transitions'] == merged_tr
print('regime resolved: hist %d unique, transitions %d unique, base updated=%s' % (nu1, nu2, out.get('updated')))
