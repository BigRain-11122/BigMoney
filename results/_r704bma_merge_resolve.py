# r704 bm-a merge resolver: 5 UU faces vs origin/main (bm-b r701/702 close + autofill waves)
# canon: per-face ts-newer-wins / append-only union / pool per-entry max-merge (MSG-0612 NULLS law)
import subprocess, json, io

def side(f, n):
    return json.loads(subprocess.run(['git', 'show', f':{n}:{f}'], capture_output=True).stdout.decode('utf-8'))

def w(f, obj):
    with io.open(f, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write('\n')
    json.load(io.open(f, encoding='utf-8'))  # reparse proof

# 1) compute_audit.json: latest ours newer (00:30:45>23:56:23); history union by ts (append-only); launches theirs (new key, empty)
o, t = side('results/compute_audit.json', 2), side('results/compute_audit.json', 3)
hist = {}
for e in o['history'] + t['history']:
    k = e.get('ts')
    if k not in hist:
        hist[k] = e
merged_hist = sorted(hist.values(), key=lambda e: e.get('ts') or '')
assert merged_hist[0].get('ts'), 'history ts sort anchor'
ca = {'latest': o['latest'], 'history': merged_hist}
if 'launches' in t:
    ca['launches'] = t['launches']
w('results/compute_audit.json', ca)
print('compute_audit: latest=ours 00:30:45; history union', len(o['history']), '+', len(t['history']), '->', len(merged_hist), '; launches kept')

# 2) futures_update_status.json: whole face ours (ts 00:31:41 > 00:01:57)
w('results/futures_update_status.json', side('results/futures_update_status.json', 2))
print('futures_update_status: ours ts-newer')

# 3) regime_state.json: ours (updated 00:30:54 > 00:11:14) + launches key theirs
o, t = side('results/regime_state.json', 2), side('results/regime_state.json', 3)
if 'launches' in t:
    o['launches'] = t['launches']
w('results/regime_state.json', o)
print('regime_state: ours ts-newer + launches kept')

# 4) token_usage.json: top ours (generated 00:32:20 > 00:02:40); machines per-machine per-key max (monotone counters)
o, t = side('results/token_usage.json', 2), side('results/token_usage.json', 3)
for m in t['machines']:
    a, b = o['machines'].get(m, {}), t['machines'][m]
    if m not in o['machines']:
        o['machines'][m] = b
    else:
        for k, v in b.items():
            if isinstance(v, (int, float)) and k in a and isinstance(a[k], (int, float)):
                a[k] = max(a[k], v)
            elif k not in a:
                a[k] = v
w('results/token_usage.json', o)
print('token_usage: top ours newer; machines per-key max union')

# 5) runnable_pool.json: 390/390 same ids; only 3 FUND-*-NULLS entries shards differ (bm-b keepalive claim-refresh fresher) -> theirs for those entries; pool top identical
# r704 fix: mutate o['entries'] LIST in place (om[i]=tm[i] rebinding the side-dict = aliasing bug, landed ours-stale face, caught by pre-push claw MSG-0612 family)
o, t = side('results/runnable_pool.json', 2), side('results/runnable_pool.json', 3)
om = {e['id']: e for e in o['entries']}
tm = {e['id']: e for e in t['entries']}
assert set(om) == set(tm), 'entry id set mismatch'
n_shard = 0
for idx, e in enumerate(o['entries']):
    if om[e['id']] != tm[e['id']]:
        o['entries'][idx] = tm[e['id']]  # in-place list mutation; theirs = fresher keepalive
        n_shard += 1
w('results/runnable_pool.json', o)
vm = {x['id']: x for x in json.load(io.open('results/runnable_pool.json', encoding='utf-8'))['entries']}
for _eid in ('FUND-VALUE-P1-NULLS', 'FUND-QUALITY-P1-NULLS', 'FUND-DIVLOWVOL-P1-NULLS'):
    assert vm[_eid]['shards'][0].get('owner_since') == tm[_eid]['shards'][0].get('owner_since'), _eid + ' owner_since must equal theirs-fresh'
print('runnable_pool: 390 entries, entries taken from theirs (in-place list mutation):', n_shard)
print('ALL 5 FACES RESOLVED')
