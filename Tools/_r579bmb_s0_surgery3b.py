# r579 bm-b surgery3b: retry-loop surgical replay for the hot window
# Policy per file: my_delta (MSG/gates) always mine; ride files in origin's
# new diff -> take origin (shared derive faces, regen-by-design), else mine.
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
print('base(merge-base)=%s' % base[:12])
old_main = run(['git', 'rev-parse', 'main']).stdout.strip()

r = run(['git', 'diff', '--name-status', base, 'main'])
my_files = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.strip()]
print('my_delta_files=%d' % len(my_files), my_files)

APPEND_ONLY = {('results', 'pool_core_samples.jsonl')}

def union_jsonl(origin_path, local_path):
    rb = subprocess.run(['git', 'show', 'origin/main:%s' % origin_path], capture_output=True)
    assert rb.returncode == 0
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
        assert isinstance(obj, dict), 'non-dict row'
        new_rows.append(l)
    ub = ob if (not ob or ob.endswith(b'\n')) else ob + b'\n'
    ub += b''.join(new_rows)
    with open(local_path, 'wb') as f:
        f.write(ub)
    return len(ol), len(new_rows)

for attempt in range(1, 7):
    run(['git', 'fetch', 'origin'], check=False)
    origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
    r = run(['git', 'diff', '--name-only', base, origin_main])
    their = set(l for l in r.stdout.splitlines() if l.strip())
    r = run(['git', 'status', '--porcelain'])
    dirty = [l[3:] for l in r.stdout.splitlines() if l[:2] in (' M', 'M ', '??')]
    keep = [f for f in dirty if f not in their]
    dropped = [f for f in dirty if f in their]
    for f in list(keep):
        parts = tuple(f.replace('/', '\\').split('\\'))
        if parts in APPEND_ONLY and f in their:
            n_o, n_new = union_jsonl(f, f)
            print('union %s: origin=%d appended=%d' % (f, n_o, n_new))
    # append-only special case: if the union file is dirty AND in their -> keep (unionized)
    # (handled above; re-check membership)
    print('attempt %d: origin=%s keep=%d take-origin=%d' % (attempt, origin_main[:10], len(keep), len(dropped)))
    tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r579b')
    env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
    run(['git', 'read-tree', origin_main], env=env)
    for f in my_files + keep:
        import glob as _g
        targets = sorted(_g.glob(f + '/**/*', recursive=True)) \
            if os.path.isdir(f) else [f]
        for t in targets:
            if os.path.isdir(t):
                continue
            h = run(['git', 'hash-object', '-w', t], env=env).stdout.strip()
            rel = os.path.relpath(t, REPO).replace('\\', '/')
            run(['git', 'update-index', '--add', '--cacheinfo',
                 '100644,%s,%s' % (h, rel)], env=env)
    tree = run(['git', 'write-tree'], env=env).stdout.strip()
    msg = ('round 579 bm-b: W92 zero-cost yield receipt + W93 seat published '
           '(replayed onto %s, attempt %d; S6 lane faces ridden) '
           '[via bm-b r579]' % (origin_main[:10], attempt))
    newc = run(['git', 'commit-tree', tree, '-p', origin_main, '-m', msg], env=env).stdout.strip()
    r = run(['git', 'push', 'origin', '%s:refs/heads/main' % newc], check=False)
    if r.returncode == 0:
        print('pushed %s (attempt %d)' % (newc[:12], attempt))
        run(['git', 'update-ref', 'refs/heads/main', newc, old_main])
        run(['git', 'reset', '--mixed', newc])
        run(['git', 'checkout', 'HEAD', '--'] + sorted(their))
        st = run(['git', 'status', '--porcelain']).stdout
        print('post dirty:')
        print(st if st else '(clean)')
        print('SURGERY3B_OK')
        sys.exit(0)
    print('push rejected (attempt %d): %s' % (attempt, r.stderr.strip()[-200:]))
    time.sleep(3)
print('SURGERY3B_EXHAUSTED')
sys.exit(2)
