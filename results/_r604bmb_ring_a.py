import subprocess, sys, json

def git(*args, **kw):
    r = subprocess.run(['git'] + list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace')
    return r

OLD = '015558245'   # origin tip at my round start = current merge-base
NEW = 'a7d3fdfb8'   # execution-time origin/main (verify at run time!)

# step 0: verify NEW is still origin/main at execution time (r593 fresh-value law)
r = git('rev-parse', 'origin/main')
cur = r.stdout.strip()
print('origin/main now:', cur)
if not cur.startswith(NEW):
    print('FATAL: origin moved again mid-ring, abort for re-plan')
    sys.exit(2)

# sanity: merge-base check
r = git('merge-base', OLD, NEW)
mb = r.stdout.strip()
print('merge-base(OLD,NEW):', mb, '== OLD:', mb == OLD)

# step 1: withdraw both local unpushed commits (content stays in tree)
r = git('reset', '--mixed', OLD)
print('reset --mixed OLD rc=', r.returncode, r.stdout.strip()[:100], r.stderr.strip()[:200])

# step 2: CAS move ref to origin tip
r = git('update-ref', 'refs/heads/main', cur, OLD)
print('update-ref rc=', r.returncode, r.stderr.strip()[:200])
if r.returncode != 0:
    print('FATAL: CAS failed (daemon may have committed mid-ring)')
    sys.exit(3)

# step 3: re-anchor index (r578: never trust checkout-after-update-ref alone)
r = git('reset', '--mixed', cur)
print('reset --mixed NEW rc=', r.returncode, r.stderr.strip()[:200])

# step 4: classify porcelain (r388: XY double-column; D rows in either column)
r = git('status', '--porcelain')
lines = [l for l in r.stdout.splitlines() if l.strip()]
keep_payload = set([
    'state.json', 'fleet/machines/bm-b.json', 'logs/iteration-loop/round_reports.md',
    'results/autofill_state.bm-b.json', 'results/runnable_pool.bm-b.json', 'results/runnable_pool.json',
])
# live-write daemon faces to keep dirty (origin did not touch them this window)
keep_dirty = {
    'results/p1d_gates.json', 'results/pool_core_samples.jsonl',
    'results/saturation_engine/face_bm-b.json', 'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
}
# in-flight product / evidence kept untracked
keep_untracked = {'results/fund_value_p1/nulls.jsonl', 'results/_r603bmb_sens_partial_killed.jsonl'}

d_restore, m_keep, other = [], [], []
for l in lines:
    xy, path = l[:2], l[3:].strip()
    if path in keep_untracked:
        continue
    if 'D' in xy:
        d_restore.append(path)          # origin-new faces my tree lacks = restore (r595)
    elif path in keep_dirty:
        m_keep.append(path)             # daemon live-write, keep dirty
    else:
        other.append((xy, path))

print('D-restore count:', len(d_restore))
print('keep-dirty count:', len(m_keep))
print('other faces (my payload + unknowns):', len(other))
for xy, p in other:
    if not (p.startswith('results/_r604') or p.startswith('docs/') or p in keep_payload
            or p.startswith('results/prospect_promotion/') or p.startswith('results/update_')
            or p in ('results/regime_state.json', 'results/regime_state.bm-b.json',
                     'results/scorecard_v1.json', 'results/strategy_scorecard.json',
                     'results/token_usage.json', 'results/token_usage.bm-b.json',
                     'results/compute_audit.json', 'results/compute_audit.bm-b.json',
                     'results/dashboard_status.json', 'results/dashboard_status.js',
                     'results/pool_dualrun.bm-b.jsonl', 'results/_attrition_guard_scan.json',
                     'results/astock_daily_update_status.json', 'results/etf_daily_pull_status.json',
                     'results/futures_update_status.json', 'results/futures_update_status.bm-b.json',
                     'results/lhb_update_status.json', 'results/lhb_update_status.bm-b.json',
                     'results/fundamental_b_layer_filter.json')):
        print('  UNKNOWN FACE needing adjudication:', xy, p)

json.dump({'d_restore': d_restore, 'keep_dirty': m_keep,
           'other': [p for _, p in other]}, open('results/_r604bmb_ring_state.json', 'w'))
print('ring phase A complete')
