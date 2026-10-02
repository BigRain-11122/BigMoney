# r588 bm-b surgical push: my committed r588 payload onto origin/main ad932f6b8 (r532/r580/r585 laws).
# Payload blobs taken from MY COMMIT ls-tree (never hash-object working tree -- r585 law).
# Triple assertions per r366: deletion-set empty x2 + tree-delta == payload.
import os, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)

def run(cmd, env=None, check=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', env=env)
    if check and r.returncode != 0:
        print('FAIL rc=%d: %s' % (r.returncode, ' '.join(cmd)))
        print(r.stderr[-600:])
        sys.exit(1)
    return r

MY_COMMIT = run(['git', 'rev-parse', 'HEAD']).stdout.strip()
BASE = run(['git', 'rev-parse', 'HEAD~1']).stdout.strip()   # 60cefd520
origin_main = run(['git', 'rev-parse', 'origin/main']).stdout.strip()
print('my=%s base=%s origin=%s' % (MY_COMMIT[:12], BASE[:12], origin_main[:12]))
assert origin_main != MY_COMMIT

# payload = my commit's delta vs its parent (49 files, blobs from MY COMMIT)
r = run(['git', 'diff', '--name-only', BASE, MY_COMMIT])
payload_files = [l.strip() for l in r.stdout.splitlines() if l.strip()]
print('payload files:', len(payload_files))

# collect blob shas from MY COMMIT tree
r = run(['git', 'ls-tree', '-r', MY_COMMIT, '--'] + payload_files)
blobs = {}
for l in r.stdout.splitlines():
    parts = l.split('\t')          # 'mode SP type SP sha TAB path' -> explicit columns (r366 law)
    meta = parts[0].split(' ')
    mode, typ, sha = meta[0], meta[1], meta[2]
    path = parts[1]
    assert typ == 'blob', 'non-blob in payload: %s' % l
    blobs[path] = (mode, sha)
assert len(blobs) == len(payload_files), 'payload blob count mismatch %d != %d' % (len(blobs), len(payload_files))

# build temp index on origin tree
tmp_index = os.path.join(REPO, '.git', 'codely-tmp-index-r588b')
if os.path.exists(tmp_index):
    os.remove(tmp_index)
env = dict(os.environ, GIT_INDEX_FILE=tmp_index)
run(['git', 'read-tree', origin_main], env=env)
for path, (mode, sha) in sorted(blobs.items()):
    run(['git', 'update-index', '--add', '--cacheinfo', '%s,%s,%s' % (mode, sha, path)], env=env)
tree = run(['git', 'write-tree'], env=env).stdout.strip()
print('new tree:', tree)

# assertion 1: deletion-set empty (origin -> new tree must contain zero D)
r = run(['git', 'diff', '--no-renames', '--name-status', origin_main, tree])
deletions = [l for l in r.stdout.splitlines() if l.startswith('D')]
assert not deletions, 'DELETION SET NOT EMPTY: %s' % deletions
changed = [l.split('\t')[-1] for l in r.stdout.splitlines() if l.strip()]
# assertion 2: tree-delta == payload exactly
assert set(changed) == set(payload_files), 'tree-delta != payload: %s' % (set(changed) ^ set(payload_files))
# assertion 3: their 2 new helper files still present in new tree
for f in ['results/_r379bmc_post_surgical_checkout.py', 'results/_r379bmc_surgical_push.py']:
    r2 = run(['git', 'ls-tree', tree, f])
    assert f in r2.stdout, 'their file missing: %s' % f
print('ASSERTIONS OK: deletions=0, tree-delta==payload(%d), their files present' % len(payload_files))

# commit-tree with my r588 message (verbatim from my commit)
r = run(['git', 'log', '--format=%B', '-n', '1', MY_COMMIT])
msg = r.stdout
new_commit = run(['git', 'commit-tree', tree, '-p', origin_main], env=dict(os.environ, GIT_AUTHOR_NAME='bm-b', GIT_AUTHOR_EMAIL='bm-b@fleet', GIT_COMMITTER_NAME='bm-b', GIT_COMMITTER_EMAIL='bm-b@fleet'), check=False)
# commit-tree reads message on stdin
import subprocess as sp
p = sp.run(['git', 'commit-tree', tree, '-p', origin_main], input=msg, capture_output=True, text=True, env=dict(os.environ, GIT_AUTHOR_NAME='bm-b', GIT_AUTHOR_EMAIL='bm-b@fleet', GIT_COMMITTER_NAME='bm-b', GIT_COMMITTER_EMAIL='bm-b@fleet'))
assert p.returncode == 0, p.stderr
new_commit = p.stdout.strip()
print('new commit:', new_commit)

# CAS update-ref: old value = full 40-char origin sha (r569-3 law)
r = run(['git', 'update-ref', 'refs/heads/main', new_commit, origin_main])
# push
r = run(['git', 'push', 'origin', 'main'], check=False)
print('push rc=%d' % r.returncode)
print(r.stdout[-500:] if r.stdout else '')
print(r.stderr[-500:] if r.stderr else '')
if r.returncode != 0:
    sys.exit(1)
# arrival self-verify (O-20261001-1108 delivery gate)
run(['git', 'fetch', 'origin'], check=False)
r = run(['git', 'rev-parse', 'origin/main'])
print('origin/main after push:', r.stdout.strip()[:12], '== new_commit'[:12], r.stdout.strip() == new_commit)
