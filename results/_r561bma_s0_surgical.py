"""r561 S0 surgical merge (bm-a) — ride commit 72baf7361 onto origin/main.

Policy per fleet law:
- 40 payload files (mine-only)  -> my blob applied verbatim
- 18 shared regen faces (both-touched, deterministic same-day regen)
    -> yield to origin side (r296-3; origin landed 06:08-06:13, fresher wall clock;
       this round's S6 chain re-derives them deterministically)
- results/pool_core_samples.jsonl (append-only jsonl) -> conflict-zone union:
    origin lines in order + my lines (vs merge-base) not byte-present in origin
    (r294 domain law: dedupe exact byte lines only)
Assertions:
- payload count == 59 (git diff --name-only vs ride parent)
- deletion set empty (r530/r516 law)
- post-write ls-tree spot checks: W54 shard-0/11 present
Zero working-tree touch (r512 backstop law); engine tick keeps writing lane files.
"""
import subprocess, sys, os

def gitb(*a):
    return subprocess.check_output(['git'] + list(a))

def gits(*a):
    return subprocess.check_output(['git'] + list(a)).decode('utf-8', 'replace')

BASE = 'bdc36af9e'          # merge-base (= ride parent)
MINE = '72baf7361'          # ride commit
ORIGIN = 'origin/main'
REGEN_YIELD = [
    'docs/daily_report/REPORT-2026-10-02.json', 'docs/daily_report/REPORT-2026-10-02.md',
    'docs/live_usage/LIVE-2026-10-02.json', 'docs/live_usage/LIVE-2026-10-02.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/dashboard_status.js', 'results/dashboard_status.json',
    'results/fundamental_b_layer_filter.json', 'results/futures_update_status.json',
    'results/lhb_update_status.json', 'results/regime_state.json',
    'results/scorecard_v1.json', 'results/strategy_scorecard.json',
    'results/token_usage.json', 'results/update_status.json',
]
POOL_JSONL = 'results/pool_core_samples.jsonl'

idx = os.path.join('.git', 'tmpidx_r561')
env = dict(os.environ, GIT_INDEX_FILE=idx)
def gidx(*a):
    return subprocess.check_output(['git'] + list(a), env=env)

# 1. temp index from origin
if os.path.exists(idx): os.remove(idx)
gidx('read-tree', ORIGIN)

# 2. payload classification
mine_payload = [f for f in gits('diff-tree', '--no-commit-id', '--name-only', '-r', BASE, MINE).split() if f]
origin_touched = set(f for f in gits('diff-tree', '--no-commit-id', '--name-only', '-r', BASE, ORIGIN).split() if f)
yield_set = set(REGEN_YIELD)
assert len(mine_payload) == 59, f'payload count {len(mine_payload)} != 59'
for f in mine_payload:
    if f == POOL_JSONL:
        continue
    if f in yield_set:
        assert f in origin_touched, f'yield file not origin-touched: {f}'
        continue  # origin side stays
    # apply my blob verbatim (mine-only file)
    assert f not in origin_touched, f'unexpected both-touched non-classified: {f}'
    blob = gits('rev-parse', f'{MINE}:{f}').strip()
    gidx('update-index', '--add', '--cacheinfo', f'100644,{blob},{f}')

# 3. pool jsonl union (conflict-zone = lines each side added vs merge-base)
def blob_lines(ref, path):
    return gitb('show', f'{ref}:{path}').splitlines(keepends=True)
base_lines = blob_lines(BASE, POOL_JSONL)
origin_lines = blob_lines(ORIGIN, POOL_JSONL)
mine_lines = blob_lines(MINE, POOL_JSONL)
base_set = set(base_lines)
origin_new = [l for l in origin_lines if l not in base_set]
mine_new = [l for l in mine_lines if l not in base_set]
seen = set(l.rstrip(b'\r\n') for l in origin_lines)
union_new = list(origin_new)
added_mine = 0
for l in mine_new:
    k = l.rstrip(b'\r\n')
    if k not in seen:
        union_new.append(l); seen.add(k); added_mine += 1
merged = b''.join([l for l in base_lines] + union_new)
print(f'pool jsonl: base={len(base_lines)} origin_new={len(origin_new)} mine_new={len(mine_new)} union_add_mine={added_mine} total={merged.count(bytes([10]))} lines')
p = subprocess.run(['git', 'hash-object', '-w', '--stdin'], input=merged, capture_output=True, check=True)
union_blob = p.stdout.decode().strip()
gidx('update-index', '--add', '--cacheinfo', f'100644,{union_blob},{POOL_JSONL}')

# 4. write tree + assertions
tree = gidx('write-tree').decode().strip()
dels = gits('diff-tree', '--no-commit-id', '--name-only', '-r', '--diff-filter=D', ORIGIN, tree).split()
assert not dels, f'DELETION SET NON-EMPTY (r530 law): {dels}'
adds = gits('diff-tree', '--no-commit-id', '--name-only', '-r', '--diff-filter=A', ORIGIN, tree).split()
print(f'tree={tree} additions={len(adds)} (expect 12 W54 shards + 5 r559 tools = 17)')
assert len(adds) == 17, f'additions {len(adds)} != 17'
for probe in ('results/p2cal_ext/n1_w54/shard-0-of-12.json', 'results/p2cal_ext/n1_w54/shard-11-of-12.json', 'results/p2cal_ext/n1_w54/shard-2-of-12.json'):
    gits('ls-tree', tree, probe)  # must exist (raises otherwise is empty output; check manually)
    out = gits('ls-tree', tree, '--', probe)
    assert out.strip(), f'missing {probe}'

# 5. commit-tree + push
msg = ('r561 S0 surgical merge: W54 12/12 harvest shard products delivered to origin '
       '(r310 completeness) + bm-a lane faces + r559 evidence tools; 18 shared regen faces '
       'yield to origin fresher wall-clock (r296-3, S6 re-derives this round); '
       'pool_core_samples conflict-zone union per r294 domain law; deletion-set asserted empty [via bm-a r561]')
sha = subprocess.check_output(['git', 'commit-tree', tree, '-p', ORIGIN, '-m', msg]).decode().strip()
print('commit:', sha)
subprocess.run(['git', 'push', 'origin', f'{sha}:main'], check=True)
print('PUSH OK')
