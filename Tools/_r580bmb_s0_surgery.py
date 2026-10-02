# r580 bm-b S0 surgery: integrate origin's new commits under live engine writers.
# Fixes vs r579 surgery3b: (1) union append-only BEFORE keep/drop split -- 3b's
# union branch was dead code (keep excludes their-files) and would drop local
# appends on checkout (r570/r524 row-loss family); (2) exclude unioned files
# from post-push checkout (preserve mid-surgery appends); (3) deletion-set
# empty assertion + payload print (r532 law); (4) handle D-files in origin diff
# (inbox MSG moves) via remove instead of checkout-fail.
import os, subprocess, sys, time, json

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-600:])
        sys.exit(1)
    return r

base = run(['git', 'merge-base', 'main', 'origin/main']).stdout.strip()
old_main = run(['git', 'rev-parse', 'main']).stdout.strip()
print('base=%s old_main=%s' % (base[:12], old_main[:12]))

r = run(['git', 'diff', '--name-status', base, 'main'])
my_files = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.strip()]
print('my_committed_delta_files=%d' % len(my_files), my_files)

APPEND_ONLY = {('results', 'pool_core_samples.jsonl')}

def union_jsonl(origin_path, local_path):
    rb = subprocess.run(['git', 'show', 'origin/main:%s' % origin_path], capture_output=True)
    assert rb.returncode == 0, 'origin blob missing for %s' % origin_path
    ob = rb.stdout
    with open(local_path, 'rb') as f:
        lb = f.read()
    ol = ob.splitlines(keepends=True)
    okeys = set(l.rstrip(b'\r\n') for l in ol if l.strip())
    new_rows = []
    for l in lb.splitlines(keepends=True):
        if not l.strip() or l.rstrip(b'\r\n') in okeys:
            continue
        obj = json.loads(l)
        assert isinstance(obj, dict), 'non-dict row in local append set'
        new_rows.append(l)
    ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
    ub += b''.join(new_rows)
    with open(local_path, 'wb') as f:
        f.write(ub)
    return len(ol), len(new_rows)

for attempt in range(1, 7):
    run(['git', 'fetch', 'origin'], check=False)
    origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
    r = run(['git', 'diff', '--no-renames', '--name-status', base, origin_main])
    their_mod, their_del = [], []
    for l in r.stdout.splitlines():
        if not l.strip():
            continue
        st = l.split('\t')[0]
        p = l.split('\t')[-1]
        (their_del if st.startswith('D') else their_mod).append(p)
    r = run(['git', 'status', '--porcelain'])
    dirty = [l[3:] for l in r.stdout.splitlines() if l[:2] in (' M', 'M ', '??')]
    # FIX vs 3b: unionize append-only dirty files that origin also touched BEFORE split
    unioned = set()
    for f in dirty:
        parts = tuple(f.replace('/', '\\').split('\\'))
        if parts in APPEND_ONLY and f in their_mod:
            n_o, n_new = union_jsonl(f, f)
            print('union %s: origin_rows=%d appended=%d' % (f, n_o, n_new))
            unioned.add(f)
    keep = [f for f in dirty if f not in their_mod or f in unioned]
    dropped = [f for f in dirty if f in their_mod and f not in unioned]
    print('attempt %d: origin=%s dirty=%d keep=%d dropped=%d their_mod=%d their_del=%d'
          % (attempt, origin_main[:10], len(dirty), len(keep), len(dropped), len(their_mod), len(their_del)))
    tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r580b')
    if os.path.exists(tmp_index):
        os.remove(tmp_index)
    env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
    run(['git', 'read-tree', origin_main], env=env)
    payload = 0
    import glob as _g
    for f in my_files + keep:
        targets = sorted(_g.glob(f + '/**/*', recursive=True)) \
            if os.path.isdir(f) else [f]
        for t in targets:
            if os.path.isdir(t):
                continue
            h = run(['git', 'hash-object', '-w', t], env=env).stdout.strip()
            rel = os.path.relpath(t, REPO).replace('\\', '/')
            run(['git', 'update-index', '--add', '--cacheinfo',
                 '100644,%s,%s' % (h, rel)], env=env)
            payload += 1
    tree = run(['git', 'write-tree'], env=env).stdout.strip()
    msg = sys.argv[1] if len(sys.argv) > 1 else (
        'round 580 bm-b: S0 integration ride (W93 shards 4-10 + engine telemetry '
        'landed; pool_core union origin-base + local dict rows per r570 law; '
        'replayed onto %s, attempt %d) [via bm-b r580]'
        % (origin_main[:10], attempt))
    proof = sys.argv[2] if len(sys.argv) > 2 else 'results/p2cal_ext/n1_w93/shard-10-of-12.json'
    newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg], env=env).stdout.strip()
    # r532 law assertions: deletion-set empty + payload count
    r = run(['git', 'diff', '--no-renames', '--name-status', origin_main, newc])
    dels = [l for l in r.stdout.splitlines() if l.startswith('D')]
    assert not dels, 'DELETION-SET NON-EMPTY: %s' % dels[:5]
    adds = [l for l in r.stdout.splitlines() if l.startswith('A')]
    mods = [l for l in r.stdout.splitlines() if l.startswith('M')]
    assert len(adds) + len(mods) <= payload, 'payload-count breach: %d+%d > %d' % (len(adds), len(mods), payload)
    print('tree_delta: A=%d M=%d D=0 payload=%d' % (len(adds), len(mods), payload))
    r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
    if r.returncode == 0:
        print('pushed %s (attempt %d)' % (newc[:12], attempt))
        run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
        run(['git', 'reset', '--mixed', newc])
        co = sorted(f for f in their_mod if f not in unioned)
        for i in range(0, len(co), 40):
            run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
        for f in their_del:
            if os.path.exists(f):
                os.remove(f)
                print('removed (origin-deleted): %s' % f)
        # delivery proof (r532 ls-tree self-attest)
        rb = subprocess.run(['git', 'ls-tree', 'origin/main', '--name-only', proof],
                            capture_output=True, text=True)
        assert proof in rb.stdout, 'DELIVERY PROOF FAIL: %s not on origin' % proof
        print('delivery proof: %s on origin' % proof)
        st = run(['git', 'status', '--porcelain']).stdout
        print('post dirty:')
        print(st if st else '(clean)')
        print('SURGERY_R580_OK')
        sys.exit(0)
    print('push rejected (attempt %d): %s' % (attempt, r.stderr.strip()[-200:]))
    time.sleep(3)
print('SURGERY_R580_EXHAUSTED')
sys.exit(2)
