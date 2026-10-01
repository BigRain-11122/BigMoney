import json, subprocess, os, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(args, env=None, inp=None):
    r = subprocess.run(['git'] + args, capture_output=True, env=env, input=inp)
    if r.returncode != 0:
        raise RuntimeError('git %s rc=%d: %s' % (args[:3], r.returncode, r.stderr.decode(errors='replace')[:400]))
    return r.stdout

APPEND_UNION = ['results/pool_core_samples.jsonl']
IDX = os.path.join(REPO, '.git', 'surgical-index-r558b')
env = os.environ.copy()
env['GIT_INDEX_FILE'] = IDX

def run(attempt):
    git(['fetch', 'origin'])
    origin = git(['rev-parse', 'origin/main']).decode().strip()
    old_base = '7657895b0'   # parent of my closeout commit
    my = git(['rev-parse', 'HEAD']).decode().strip()
    payload = [p for p in git(['diff', '--name-only', old_base, my]).decode().split() if p]
    if 'results/_r558bmb_closeout_push.py' not in payload:
        payload.append('results/_r558bmb_closeout_push.py')
    print('attempt %d: origin=%s payload=%d files' % (attempt, origin[:9], len(payload)))

    open(IDX, 'wb').close()
    git(['read-tree', origin], env=env)

    def add_payload(path):
        r = subprocess.run(['git', 'cat-file', '-e', '%s:%s' % (my, path)],
                           capture_output=True, env=env)
        if r.returncode == 0:
            blob = git(['rev-parse', '%s:%s' % (my, path)]).decode().strip()
        else:
            blob = git(['hash-object', '-w', path], env=env).decode().strip()
        git(['update-index', '--add', '--cacheinfo', '100644,%s,%s' % (blob, path)], env=env)

    for p in payload:
        if p in APPEND_UNION:
            o_lines = git(['show', 'origin/main:' + p]).splitlines(keepends=True)
            m_lines = git(['show', '%s:%s' % (my, p)]).splitlines(keepends=True)
            o_set = set(x.strip() for x in o_lines)
            new = [x for x in m_lines if x.strip() not in o_set]
            content = b''.join(o_lines) + b''.join(new)
            h = git(['hash-object', '-w', '--stdin'], env=env, inp=content).decode().strip()
            git(['update-index', '--add', '--cacheinfo', '100644,%s,%s' % (h, p)], env=env)
            print('  union %s: origin %d + mine-new %d' % (p, len(o_lines), len(new)))
        else:
            add_payload(p)

    tree = git(['write-tree'], env=env).decode().strip()
    diff = git(['diff-tree', '-r', '--name-status', origin, tree]).decode()
    lines = [l for l in diff.splitlines() if l.strip()]
    dels = [l for l in lines if l.startswith('D')]
    assert not dels, 'DELETION SET non-empty: %s' % dels
    changed = set(l.split('\t')[-1] for l in lines)
    assert changed == set(payload), 'changed mismatch extra=%s missing=%s' % (changed - set(payload), set(payload) - changed)
    print('  deletion-set empty, payload count OK (%d)' % len(payload))

    msg = git(['log', '-1', '--format=%B', my]).decode().strip()
    commit = git(['commit-tree', tree, '-p', origin, '-m', msg], env=env).decode().strip()
    r = subprocess.run(['git', 'update-ref', 'refs/heads/main', commit, my], capture_output=True)
    if r.returncode != 0:
        print('  CAS failed, refetch needed')
        return False
    subprocess.run(['git', 'checkout', '-f', 'main'], capture_output=True)
    pr = subprocess.run(['git', 'push', 'origin', 'main'], capture_output=True)
    if pr.returncode == 0:
        print('  PUSH OK, closeout commit=%s (reparented onto %s)' % (commit[:9], origin[:9]))
        return True
    print('  push rejected: %s' % pr.stderr.decode(errors='replace')[:200])
    return False

for att in (1, 2, 3):
    if run(att):
        break
else:
    sys.exit('PUSH FAILED after 3 attempts')

git(['fetch', 'origin'])
behind = git(['rev-list', '--count', 'HEAD..origin/main']).decode().strip()
ahead = git(['rev-list', '--count', 'origin/main..HEAD']).decode().strip()
n51 = len(git(['ls-tree', '--name-only', 'origin/main', 'results/p2cal_ext/n1_w51/']).decode().split())
print('delivery self-check: behind=%s ahead=%s | origin n1_w51 shards=%d' % (behind, ahead, n51))
assert n51 == 12, 'bm-c W51 products must remain 12/12 on origin'
git(['cat-file', '-e', 'origin/main:results/perpetual_faces/n1_w49_results.json'])
print('n1_w49_results.json on origin: OK | CLOSEOUT DELIVERY COMPLETE')
