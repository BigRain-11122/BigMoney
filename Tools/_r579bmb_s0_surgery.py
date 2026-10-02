# r579 bm-b S0 surgical integration (r532 live-writer law / r570 origin-union law)
# - validate W91 shard products 5..11 parse as dict JSON
# - pool_core_samples.jsonl: origin verbatim base + local rows not in origin (dict-type gate)
# - temp-index surgery: read-tree origin/main, overlay this machine's files, commit-tree -p origin/main, push
# - post-push: CAS update-ref, reset --mixed, checkout origin-side files
import json, os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-800:])
        sys.exit(1)
    return r

def run_bytes(cmd, env=None):
    return subprocess.run(cmd, capture_output=True, env=env)

SHARDS = ['results/p2cal_ext/n1_w91/shard-%d-of-12.json' % i for i in range(5, 12)]
LANE_FILES = [
    'results/autofill_state.bm-b.json',
    'results/p1d_gates.json',
    'results/pool_core_samples.jsonl',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-b.json',
] + SHARDS

# 1. shard product sanity (dict JSON, audit block present)
for p in SHARDS:
    with open(p, 'rb') as f:
        obj = json.loads(f.read())
    assert isinstance(obj, dict), p
    assert 'audit' in obj, 'no audit block: ' + p
print('LEG1 shards_ok=7')

# 2. pool_core_samples origin-union
r = run_bytes(['git', 'show', 'origin/main:results/pool_core_samples.jsonl'])
assert r.returncode == 0, 'origin show failed'
origin_b = r.stdout
with open('results/pool_core_samples.jsonl', 'rb') as f:
    local_b = f.read()
ol = origin_b.splitlines(keepends=True)
ll = local_b.splitlines(keepends=True)
o_keys = set(l.rstrip(b'\r\n') for l in ol if l.strip())
new_rows = []
for l in ll:
    if not l.strip():
        continue
    if l.rstrip(b'\r\n') in o_keys:
        continue
    obj = json.loads(l)  # parse gate
    assert isinstance(obj, dict), 'non-dict row: ' + l[:100].decode('utf-8', 'replace')
    new_rows.append(l)
union_b = origin_b if origin_b.endswith(b'\n') or not origin_b else origin_b + b'\n'
union_b += b''.join(new_rows)
with open('results/pool_core_samples.jsonl', 'wb') as f:
    f.write(union_b)
print('LEG2 union origin_rows=%d local_rows=%d appended=%d' % (len(ol), len(ll), len(new_rows)))

# 3. temp-index surgery
old_main = run(['git', 'rev-parse', 'main']).stdout.strip()
origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r579')
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin_main], env=env)
for f in LANE_FILES:
    h = run(['git', 'hash-object', '-w', f], env=env).stdout.strip()
    run(['git', 'update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, f)], env=env)
tree = run(['git', 'write-tree'], env=env).stdout.strip()
msg = ('round 579 bm-b S0: surgical integration onto %s '
       '(W91 shards 5-11 + engine/autofill telemetry + pool_core_samples origin-union) '
       '[via bm-b r579]' % origin_main[:10])
newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg], env=env).stdout.strip()
print('LEG3 tree=%s new=%s' % (tree[:12], newc[:12]))

# 4. push (fast-forward by construction)
r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
if r.returncode != 0:
    print('PUSH_REJECTED: ' + r.stderr[-500:])
    sys.exit(2)
print('LEG4 pushed %s' % newc[:12])

# 5. re-anchor local main (CAS old value, full 40 chars per r569-iii)
run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
run(['git', 'reset', '--mixed', newc])
ORIGIN_SIDE = [
    'research/PERPETUAL_FACES.md', 'research/PERPETUAL_N1_W88_PREREG.md', 'research/PERPETUAL_N1_W90_PREREG.md',
    'results/autofill_state.bm-a.json', 'results/autofill_state.bm-c.json',
    'results/dispatcher_state.bm-c.json', 'results/fund_history_status.json',
    'results/p2cal_ext/n1_w90', 'results/perpetual_faces/n1_w88_results.json',
    'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/face_bm-c.json',
    'results/saturation_engine/history_bm-a.jsonl', 'results/saturation_engine/state_bm-a.json',
    'results/saturation_engine_state.bm-c.json',
    'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
]
run(['git', 'checkout', 'HEAD', '--'] + ORIGIN_SIDE)
st = run(['git', 'status', '--porcelain']).stdout
print('LEG5 re-anchored; dirty_now:')
print(st if st else '(clean)')

# 6. product completeness on origin (r310 law, pre-finalize)
for d, expect in [('results/p2cal_ext/n1_w89', 12), ('results/p2cal_ext/n1_w91', 12)]:
    r = run(['git', 'ls-tree', '--name-only', 'origin/main', d + '/'])
    n = len([x for x in r.stdout.splitlines() if x.strip()])
    print('LEG6 %s on-origin=%d/%d' % (d, n, expect))
    assert n == expect, 'product completeness FAIL ' + d
print('SURGERY_OK')
