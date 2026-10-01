import json, subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(args, env=None, inp=None):
    r = subprocess.run(['git'] + args, capture_output=True, env=env, input=inp)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d: %s' % (args[:3], r.returncode, r.stderr.decode(errors='replace')[:500]))
    return r.stdout

W49_SHARDS = [f'results/p2cal_ext/n1_w49/shard-{i}-of-12.json' for i in range(2, 12)]
W49_FINAL = ['results/perpetual_faces/n1_w49_results.json']
PREREG = ['research/PERPETUAL_N1_W49_PREREG.md']
LANE_EXACT = [
    'results/pool_dualrun.bm-b.jsonl',
    'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/state_bm-b.json',
    'results/autofill_state.bm-b.json',
    'results/compute_audit.bm-b.json',
    'results/etf_daily_pull_status.json',
    'results/futures_update_status.bm-b.json',
    'results/lhb_update_status.bm-b.json',
    'results/regime_state.bm-b.json',
    'results/token_usage.bm-b.json',
    'results/update_status.bm-b.json',
    'results/_r556bmb_codely_struct.py',
    'results/_r556bmb_monthly.py',
    'results/_r556bmb_s6_chain.py',
    'results/_r556bmb_w49nums.py',
    'results/_r558bmb_s0.py',
]
APPEND_UNION = [
    'results/pool_core_samples.jsonl',
    'results/saturation_engine/ledger_bm-b.jsonl',
]
EXPECTED = set(W49_SHARDS + W49_FINAL + PREREG + LANE_EXACT + APPEND_UNION)

# sanity gates before building
assert len([f for f in os.listdir('results/p2cal_ext/n1_w49') if f.endswith('.json')]) == 12, 'shard count != 12'
res = json.load(open('results/perpetual_faces/n1_w49_results.json', encoding='utf-8'))
lg = res['science_gates']['ledger']
assert (lg['prev_total'], lg['batch_trials'], lg['total']) == (467948, 2200, 470148), lg

IDX = os.path.join(REPO, '.git', 'surgical-index-r558')
env = os.environ.copy()
env['GIT_INDEX_FILE'] = IDX

def build_and_push(attempt):
    git(['fetch', 'origin'])
    origin = git(['rev-parse', 'origin/main']).decode().strip()
    old_head = git(['rev-parse', 'refs/heads/main']).decode().strip()
    # local main must be ancestor of origin/main
    base = git(['merge-base', old_head, origin]).decode().strip()
    assert base == old_head, 'local main not ancestor of origin/main -> need resolver route, abort'

    open(IDX, 'wb').close()
    git(['read-tree', origin], env=env)

    def add_blob(path, content):
        h = git(['hash-object', '-w', '--stdin'], env=env, inp=content).decode().strip()
        git(['update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, path)], env=env)

    for p in W49_SHARDS + W49_FINAL + PREREG + LANE_EXACT:
        add_blob(p, open(p, 'rb').read())
    for p in APPEND_UNION:
        o_lines = git(['show', 'origin/main:' + p]).splitlines(keepends=True)
        l_lines = open(p, 'rb').read().splitlines(keepends=True)
        o_set = set(x.strip() for x in o_lines)
        new = [x for x in l_lines if x.strip() not in o_set]
        add_blob(p, b''.join(o_lines) + b''.join(new))
        print('  union %s: origin %d + local-new %d' % (p, len(o_lines), len(new)))

    tree = git(['write-tree'], env=env).decode().strip()
    diff = git(['diff-tree', '-r', '--name-status', origin, tree]).decode()
    lines = [l for l in diff.splitlines() if l.strip()]
    dels = [l for l in lines if l.startswith('D')]
    assert not dels, 'DELETION SET non-empty: %s' % dels
    changed = set(l.split('\t')[-1] for l in lines)
    assert changed == EXPECTED, 'changed mismatch extra=%s missing=%s' % (changed - EXPECTED, EXPECTED - changed)
    print('  payload count OK: %d, deletion set empty' % len(EXPECTED))

    msg = ('r558 S0 surgical delivery: W49 12/12 product shards + n1_w49_results.json FINALIZE one-pass '
           '(ledger 467,948+2,200=470,148, prev=W47 head origin-timing derive, seat ahead of in-flight W48/W50 per r518 law) '
           '+ prereg s7/s8 backfill (S5 4/4 PASS, K=103,520==sec0 projection, r538 one-pass, r307 two-state) '
           '+ engine lane faces (ledger_bm-b +9 union, history tail window, face/state/autofill/compute_audit bm-b) '
           '+ append unions (pool_core_samples +10, dualrun tail) + tools; shared regen faces left to origin side [via bm-b r558]')
    commit = git(['commit-tree', tree, '-p', origin, '-m', msg], env=env).decode().strip()

    r = subprocess.run(['git', 'update-ref', 'refs/heads/main', commit, old_head], capture_output=True)
    if r.returncode != 0:
        print('  CAS failed (main moved by daemon?), retrying with fresh origin')
        return False
    subprocess.run(['git', 'checkout', '-f', 'main'], capture_output=True)
    pr = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
    if pr.returncode == 0:
        print('  PUSH OK, commit=%s' % commit)
        return True
    print('  push rejected: %s' % pr.stderr.decode(errors='replace')[:300])
    return False

for att in range(1, 4):
    print('attempt', att)
    if build_and_push(att):
        break
else:
    sys.exit('PUSH FAILED after 3 attempts')

# delivery self-check
git(['fetch', 'origin'])
n = len(git(['ls-tree', '--name-only', 'origin/main', 'results/p2cal_ext/n1_w49/']).decode().split())
print('origin W49 shards after push:', n)
git(['cat-file', '-e', 'origin/main:results/perpetual_faces/n1_w49_results.json'])
print('n1_w49_results.json ON ORIGIN: OK')
behind = git(['rev-list', '--count', 'HEAD..origin/main']).decode().strip()
print('local behind origin:', behind)
print('SURGICAL DELIVERY COMPLETE')
