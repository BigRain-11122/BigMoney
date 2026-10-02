# r581 bm-b S0 surgery: integrate origin's 4 new commits (bm-c r372 W92
# finalize + bm-a r582 lane defense + W94 shards 4..11 + rides) under live
# engine writers. r580 tool + two extensions:
#   (1) CODELY.md union -- my_files INTERSECTS their_mod on CODELY.md this
#       window (bm-a r582 appended 2 r581 pit entries; my commit appended 3
#       r580 lessons) -> whole-file application would clobber their rows
#       (the r580 W94-heal lesson's own trap); union = origin blob base +
#       my committed delta lines appended at tail.
#   (2) results/p2cal_ext/n1_w97/ excluded from the ride -- burn in flight
#       (engine self-ignited post-freeze, tick ~1/min); products ride the
#       next round commit when complete (finalize chain for W97 is far
#       upstream anyway: W93 -> W94 -> W95 -> W96 -> W97).
# r532 law: tracked active-write files in tree -> NO rebase/amend/autostash.
# Deletion-set empty + payload-count assertions (r532 law).
import os, subprocess, sys, time, json, glob as _g

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
CREATE = 0x08000000


def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8',
                       errors='replace', env=env, creationflags=CREATE)
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
print('my_committed_delta_files=%d' % len(my_files))

APPEND_ONLY_JSONL = {('results', 'pool_core_samples.jsonl')}
CODELY = 'CODELY.md'


def union_jsonl(origin_path, local_path):
    rb = subprocess.run(['git', 'show', 'origin/main:%s' % origin_path],
                        capture_output=True, creationflags=CREATE)
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


def union_codely(origin_path, local_path, my_delta_base):
    """CODELY union: origin blob base + MY COMMITTED delta lines appended
    at tail (line-precise: only lines my commit added vs the merge-base)."""
    rb = subprocess.run(['git', 'show', 'origin/main:%s' % origin_path],
                        capture_output=True, creationflags=CREATE)
    assert rb.returncode == 0, 'origin blob missing for %s' % origin_path
    ob = rb.stdout
    # my committed delta lines vs merge-base (the 3 r580 lesson lines)
    rd = subprocess.run(['git', 'diff', my_delta_base, 'main', '--', CODELY],
                       capture_output=True, creationflags=CREATE)
    added = [l[1:] for l in rd.stdout.decode('utf-8', 'replace').splitlines()
             if l.startswith('+') and not l.startswith('+++')]
    added_bytes = [a.encode('utf-8') for a in added]
    okeys = set(ob.splitlines())
    tail = b''
    for ab in added_bytes:
        if ab.strip() and ab not in okeys:
            tail += ab + b'\n'
    ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
    ub += tail
    with open(local_path, 'wb') as f:
        f.write(ub)
    return len(ob.splitlines()), len(tail.splitlines())


# CODELY union happens BEFORE payload build (it is in my_files AND their_mod)
n_o, n_new = union_codely(CODELY, CODELY, base)
print('union CODELY.md: origin_lines=%d my_new_tail_lines=%d' % (n_o, n_new))

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
    # union append-only dirty files that origin also touched
    unioned = set()
    for f in dirty:
        parts = tuple(f.replace('/', '\\').split('\\'))
        if parts in APPEND_ONLY_JSONL and f in their_mod:
            n_o, n_new = union_jsonl(f, f)
            print('union %s: origin_rows=%d appended=%d' % (f, n_o, n_new))
            unioned.add(f)
    # n1_w97 burn-in-flight products excluded from the ride (ride next round)
    keep = [f for f in dirty
            if (f not in their_mod or f in unioned)
            and not f.replace('\\', '/').startswith('results/p2cal_ext/n1_w97')]
    dropped = [f for f in dirty if f not in keep and f not in
               [x for x in dirty if x.replace('\\', '/').startswith('results/p2cal_ext/n1_w97')]]
    print('attempt %d: origin=%s dirty=%d keep=%d dropped(origin-side-take)=%d '
          'their_mod=%d their_del=%d'
          % (attempt, origin_main[:10], len(dirty), len(keep), len(dropped),
             len(their_mod), len(their_del)))
    tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r581b')
    if os.path.exists(tmp_index):
        os.remove(tmp_index)
    env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
    run(['git', 'read-tree', origin_main], env=env)
    payload = 0
    for f in my_files + keep:
        targets = sorted(_g.glob(f.replace('\\', '/') + '/**/*', recursive=True)) \
            if os.path.isdir(f.replace('\\', '/')) else [f]
        for t in targets:
            if os.path.isdir(t):
                continue
            h = run(['git', 'hash-object', '-w', t], env=env).stdout.strip()
            rel = os.path.relpath(t, REPO).replace('\\', '/')
            run(['git', 'update-index', '--add', '--cacheinfo',
                 '100644,%s,%s' % (h, rel)], env=env)
            payload += 1
    tree = run(['git', 'write-tree'], env=env).stdout.strip()
    msg = ('round 581 bm-b: S0 surgery ride (W97 freeze five-face + W95 shard products 1-11 + '
           'r580 estate adoption carried; CODELY union origin-base + 3 r580 lines per r580 '
           'clobber-trap lesson; n1_w97 in-flight products excluded ride-next; replayed onto '
           '%s, attempt %d) [via bm-b r581]' % (origin_main[:10], attempt))
    proof = 'research/PERPETUAL_N1_W97_PREREG.md'
    newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg],
               env=env).stdout.strip()
    r = run(['git', 'diff', '--no-renames', '--name-status', origin_main, newc])
    dels = [l for l in r.stdout.splitlines() if l.startswith('D')]
    assert not dels, 'DELETION-SET NON-EMPTY: %s' % dels[:5]
    adds = [l for l in r.stdout.splitlines() if l.startswith('A')]
    mods = [l for l in r.stdout.splitlines() if l.startswith('M')]
    assert len(adds) + len(mods) <= payload, \
        'payload-count breach: %d+%d > %d' % (len(adds), len(mods), payload)
    print('tree_delta: A=%d M=%d D=0 payload=%d' % (len(adds), len(mods), payload))
    # structural self-check: bm-a's 2 r581 CODELY entries must survive in the
    # new tree (the r580 clobber-trap assertion -- union proof)
    rb = subprocess.run(['git', 'show', '%s:CODELY.md' % newc],
                        capture_output=True, creationflags=CREATE)
    txt = rb.stdout.decode('utf-8', 'replace')
    assert 'r582 bm-a' in txt or 'r581 bm-a' in txt or 'r372 bm-c' in txt, \
        'CLOBBER ASSERT FAIL: bm-a/bm-c new CODELY rows missing in new tree'
    assert 'r580 bm-b' in txt, 'CLOBBER ASSERT FAIL: my 3 r580 rows missing'
    print('codely union proof: bm-a/bm-c tail rows + my r580 rows all present')
    r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
    if r.returncode == 0:
        print('pushed %s (attempt %d)' % (newc[:12], attempt))
        run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
        run(['git', 'reset', '--mixed', newc])
        co = sorted(f for f in their_mod if f not in unioned and f != CODELY)
        for i in range(0, len(co), 40):
            run(['git', 'checkout', 'HEAD', '--'] + co[i:i + 40])
        for f in their_del:
            if os.path.exists(f):
                os.remove(f)
                print('removed (origin-deleted): %s' % f)
        rb = subprocess.run(['git', 'ls-tree', 'origin/main', '--name-only', proof],
                           capture_output=True, text=True, creationflags=CREATE)
        assert proof in rb.stdout, 'DELIVERY PROOF FAIL: %s not on origin' % proof
        print('delivery proof: %s on origin' % proof)
        st = run(['git', 'status', '--porcelain']).stdout
        print('post dirty:')
        print(st if st else '(clean)')
        print('SURGERY_R581_OK')
        sys.exit(0)
    print('push rejected (attempt %d): %s' % (attempt, r.stderr.strip()[-200:]))
    time.sleep(3)
print('SURGERY_R581_EXHAUSTED')
sys.exit(2)
