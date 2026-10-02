# r575 bm-b S0 recovery integration (dead-r574 session adoption, r529 law):
# local main == 45e05a67c (fully pushed, 0 ahead); origin/main 6 ahead.
# Dirty tree = dead session's uncommitted S6 faces + engine telemetry + W82 burn
# products. No divergence -> surgical diff-based payload (r530 law), no rebase.
#
# KEEP (working-tree wins):
#   - W82 12/12 shards (untracked, audit.machine=bm-b pre-verified)
#   - _r574bmb_s6_driver.py (dead-session tool archive, r322 law)
#   - scripts/perpetual_faces.py + perpetual_faces_n1.py: TAKE ORIGIN -- bm-c
#     r365 same-window already healed my W82 rows (r519 family 9th occurrence,
#     byte-restore from holding commit 45e05a67c) and added W83 rows; local
#     copies are now stale (numstat origin==local+31/+200 additions, 0 del).
#   - bm-b lane telemetry (single-writer, ledger verified pure superset)
#   - dead-session S6 shared regen faces (wall-clock 12:22-12:29 newer than
#     bm-a's cbb803728 12:21:41, r505 take-new law)
#   - pool_core_samples.jsonl -> line-level union origin + local-only dict rows
# TAKE ORIGIN (materialize): canon PERPETUAL_FACES.md (has bm-a W81 row), CODELY,
#   W81 products/results, host-guarded faces (bm-a), all peer lane files.
import subprocess, sys, os, json, glob, datetime
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # repo root

OLD_HEAD = '45e05a67c'
PEER_S6_TS = 1730000000  # placeholder, replaced by parse below

def git(args, **kw):
    return subprocess.run(['git'] + args, capture_output=True, **kw)

def gb(ref):
    r = git(['show', ref])
    assert r.returncode == 0, (ref, r.stderr[:300])
    return r.stdout

def lock_retry(args):
    for i in range(4):
        r = git(args)
        if r.returncode == 0 or b'index.lock' not in r.stderr:
            return r
        import time; time.sleep(2)
    return r

# ---- 1. preconditions ----
r = git(['rev-parse', 'HEAD']); assert r.returncode == 0
head = r.stdout.decode().strip()
assert head.startswith(OLD_HEAD), f'HEAD moved: {head}'
r = lock_retry(['fetch', 'origin']); assert r.returncode == 0, r.stderr[:300]
r = git(['rev-parse', 'origin/main']); assert r.returncode == 0
origin = r.stdout.decode().strip()
r = git(['merge-base', '--is-ancestor', 'HEAD', 'origin/main'])
assert r.returncode == 0, 'local diverged from origin -- abort (protocol: read-only round)'
print(f'[1] head={head[:9]} origin={origin[:9]} behind={git(["rev-list","--count",f"HEAD..{origin}"]).stdout.decode().strip()}')

# origin-touched file list
r = git(['diff', '--name-only', 'HEAD', origin]); assert r.returncode == 0
origin_touched = [l.strip() for l in r.stdout.decode().splitlines() if l.strip()]
print(f'[1] origin_touched={len(origin_touched)}')

# ---- 2. keep-set definition ----
keep = []
keep += sorted(glob.glob('results/p2cal_ext/n1_w82/*.json'))
keep += ['results/_r574bmb_s6_driver.py']
keep += ['results/saturation_engine/face_bm-b.json',
         'results/saturation_engine/history_bm-b.jsonl',
         'results/saturation_engine/ledger_bm-b.jsonl',
         'results/saturation_engine/state_bm-b.json',
         'results/autofill_state.bm-b.json', 'results/compute_audit.bm-b.json',
         'results/fundamental_status.bm-b.json', 'results/futures_update_status.bm-b.json',
         'results/lhb_update_status.bm-b.json', 'results/minute_feed_status.bm-b.json',
         'results/regime_state.bm-b.json', 'results/token_usage.bm-b.json',
         'results/update_status.bm-b.json', 'results/pool_dualrun.bm-b.jsonl',
         'results/astock_daily_update_status.json', 'results/etf_daily_pull_status.json']

# shared regen faces: keep only if local wall-clock newer than peer's last
# chain commit (cbb803728 2026-10-02 12:21:41 +0800)
PEER_TS = int(datetime.datetime(2026, 10, 2, 12, 21, 41).timestamp())
shared = ['docs/daily_report/REPORT-2026-10-02.json', 'docs/daily_report/REPORT-2026-10-02.md',
          'docs/live_usage/LIVE-2026-10-02.json', 'docs/live_usage/LIVE-2026-10-02.md',
          'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
          'results/compute_audit.json', 'results/token_usage.json', 'results/update_status.json',
          'results/regime_state.json', 'results/fundamental_status.json',
          'results/futures_update_status.json', 'results/lhb_update_status.json',
          'results/minute_feed_status.json', 'results/fundamental_b_layer_filter.json',
          'data/fundamental/eligibility.csv', 'results/p1d_gates.json']
for f in shared:
    m = os.path.getmtime(f)
    tag = 'KEEP(newer)' if m > PEER_TS else 'TAKE-ORIGIN(stale)'
    print(f'[2] {tag} mtime={datetime.datetime.fromtimestamp(m):%H:%M:%S} {f}')
    if m > PEER_TS:
        keep.append(f)
keep = sorted(set(f.replace('\\', '/') for f in keep))
for f in keep:
    assert os.path.exists(f), f'missing keep file {f}'
print(f'[2] keep_total={len(keep)} (new={len(glob.glob("results/p2cal_ext/n1_w82/*.json"))+1} existing={len(keep)-len(glob.glob("results/p2cal_ext/n1_w82/*.json"))-1})')

# ---- 3. heal verification (bm-c r365 restored my W82 rows; local now stale) ----
for f in ['scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py']:
    r = git(['diff', '--numstat', 'origin/main', '--', f])
    parts = r.stdout.decode().split()
    a, d = int(parts[0]), int(parts[1])
    assert a == 0, f'{f}: local has {a} lines origin lacks -- W82 row heal incomplete, abort'
    print(f'[3] {f}: local adds 0 vs origin (W82 rows intact per bm-c r365 heal); origin ahead +{d} lines (W83) -> TAKE ORIGIN')

# ---- 4. pool_core_samples union (r570 dict-only line union) ----
PCS = 'results/pool_core_samples.jsonl'
ob = gb(origin + ':' + PCS)
lb = open(PCS, 'rb').read()
ol = ob.splitlines(keepends=True); ll = lb.splitlines(keepends=True)
okeys = {l.rstrip(b'\r\n') for l in ol}
common = sum(1 for l in ll if l.rstrip(b'\r\n') in okeys)
local_only = [l for l in ll if l.rstrip(b'\r\n') not in okeys]
assert common >= len(ol) * 0.5, f'overlap suspicious: {common}/{len(ol)}'
for l in local_only:
    v = json.loads(l.decode('utf-8'))
    assert isinstance(v, dict), 'non-dict local row -- r570 law abort'
merged = ob + (b'' if ob.endswith(b'\n') or not ob else b'\n') + b''.join(local_only)
open(PCS, 'wb').write(merged)
nl = len(open(PCS, 'rb').read().splitlines())
print(f'[4] pool_core_samples: origin={len(ol)} local={len(ll)} common={common} appended={len(local_only)} final={nl} (dict-only verified)')
keep.append(PCS)

# ---- 5. build surgical tree on origin/main ----
msg = ("round 575 bm-b S0 recovery integrate: adopt dead-r574 W82 burn 12/12 shards "
       "(audit.machine=bm-b verified; W82 registration rows already healed by bm-c r365 "
       "same-window, verified byte-intact) + dead-session S6 faces (wall-clock newer) + "
       "engine telemetry lane; pool_core_samples line-union origin+local dict-only; "
       "take-origin: canon, pf scripts (W83 rows), W81 products, CODELY, host-guarded "
       "faces [via bm-b r575]")
new_sha = None
for attempt in range(1, 5):
    idx = os.path.join(os.environ.get('TEMP', '.'), '_r575bmb_idx')
    env = dict(os.environ); env['GIT_INDEX_FILE'] = idx
    if os.path.exists(idx): os.remove(idx)
    r = subprocess.run(['git', 'read-tree', origin], capture_output=True, env=env)
    assert r.returncode == 0, r.stderr[:300]
    for f in keep:
        rr = subprocess.run(['git', 'hash-object', '-w', '--', f], capture_output=True)
        assert rr.returncode == 0, (f, rr.stderr[:200])
        sha = rr.stdout.decode().strip()
        rr = subprocess.run(['git', 'update-index', '--add', '--cacheinfo',
                             f'100644,{sha},{f}'], capture_output=True, env=env)
        assert rr.returncode == 0, (f, rr.stderr[:200])
    # payload assertions (r530/r568): cached diff vs origin -- no deletions, exact keep set
    rr = subprocess.run(['git', 'diff-index', '--cached', '--name-status', origin],
                        capture_output=True, env=env)
    assert rr.returncode == 0, rr.stderr[:300]
    lines = [l.split('\t') for l in rr.stdout.decode().splitlines() if l.strip()]
    dels = [p for st, p in lines if st.startswith('D')]
    assert not dels, f'DELETION SET non-empty (r530 law abort): {dels[:5]}'
    changed = {p for _, p in lines}
    expect = set(keep) | {k for k in keep}
    missing = changed - expect
    assert not missing, f'unexpected payload entries: {sorted(missing)[:5]}'
    print(f'[5] attempt{attempt} payload={len(lines)} entries, deletions=0, set==keep')
    rr = subprocess.run(['git', 'write-tree'], capture_output=True, env=env)
    assert rr.returncode == 0, rr.stderr[:200]
    tree = rr.stdout.decode().strip()
    rr = subprocess.run(['git', 'commit-tree', tree, '-p', origin, '-m', msg],
                        capture_output=True)
    assert rr.returncode == 0, rr.stderr[:200]
    cand = rr.stdout.decode().strip()
    # final deletion gate on the actual commit (r530 mirror leg)
    rr = git(['diff-tree', '--diff-filter=D', '--name-only', origin, cand])
    assert rr.returncode == 0 and not rr.stdout.strip(), f'commit deletes files: {rr.stdout[:300]}'
    # CAS move main
    cas_old = head if attempt == 1 else new_sha
    rr = git(['update-ref', 'refs/heads/main', cand, cas_old])
    assert rr.returncode == 0, f'CAS failed (ref moved): {rr.stderr[:200]}'
    new_sha = cand
    rr = git(['push', 'origin', f'{new_sha}:refs/heads/main'])
    if rr.returncode == 0:
        print(f'[5] PUSHED {new_sha[:9]}')
        break
    print(f'[5] push rejected (attempt {attempt}): {rr.stderr[:200]}')
    r = git(['fetch', 'origin']); assert r.returncode == 0
    origin = git(['rev-parse', 'origin/main']).stdout.decode().strip()
    head = new_sha
else:
    raise SystemExit('push rejected twice -- abort for human/lane review')

# ---- 6. align working tree (reset --mixed + materialize origin-owned faces) ----
r = git(['reset', '--mixed', new_sha]); assert r.returncode == 0, r.stderr[:200]
mat = [f for f in origin_touched if f not in set(keep)]
if mat:
    r = git(['checkout', '--'] + mat)
    assert r.returncode == 0, r.stderr[:300]
print(f'[6] materialized {len(mat)} origin-owned faces')
r = git(['status', '--porcelain'])
st = r.stdout.decode().splitlines()
dels = [l for l in st if l.startswith(' D') or l.startswith('D ')]
assert not dels, f'phantom-D remains (r354 law): {dels[:5]}'
print(f'[6] post status entries={len(st)} (fresh engine writes expected):')
for l in st[:12]: print('   ', l)
r = git(['ls-tree', '--name-only', 'origin/main', 'results/p2cal_ext/n1_w82/'])
n = len([l for l in r.stdout.decode().splitlines() if l.strip()])
assert n == 12, f'origin n1_w82 count {n} != 12'
print(f'[6] origin ls-tree n1_w82 = {n}/12 (r310 gate ready)')
print('[DONE] integration complete')
