# -*- coding: utf-8 -*-
"""r589 bm-a realign pass 2 (correction): filter-safe face classification.
M-face staleness = `git diff --quiet OLD -- path` (git-side filtered compare,
CRLF-safe per r530/r373 blob-space law), NOT raw hash-object. File-move pairs
(D processed/ + ?? inbox/) resolved per r586 law: blob-identity proof then
restore canonical + delete stale untracked copy. Live-write faces preserved.
"""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
NEW = 'ff0b1869b141c06cf6bf226df3f37e9a2ff91762'
OLD = '1699ff61e'

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True)
    if check and r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:5], r.stderr.decode('utf-8', 'replace')[-400:]))
    return r.stdout

def rc(cmd):
    return subprocess.run(cmd, capture_output=True)

# sanity: ref/index already re-anchored by pass 1
head = run(['git', 'rev-parse', 'HEAD']).decode().strip()
assert head == NEW, 'HEAD drifted: ' + head

out = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
restore, preserve, moves = [], [], []
for line in out.splitlines():
    if not line.strip():
        continue
    st, path = line[:2], line[3:].strip().strip('"')
    if st == '??':
        # file-move pair candidate: untracked copy where OLD tracked it
        r = rc(['git', 'cat-file', '-e', OLD + ':' + path])
        if r.returncode == 0:
            moves.append(path)
        else:
            preserve.append(('untracked-new', path))
        continue
    if st.endswith('D'):
        restore.append(path)   # missing from worktree -> restore from NEW
        continue
    if st.endswith('M'):
        # filtered compare vs OLD base (CRLF-safe)
        r = rc(['git', 'diff', '--quiet', OLD, '--', path])
        if r.returncode == 0:
            restore.append(path)   # stale copy of OLD -> restore from NEW
        else:
            preserve.append(('live-write', path))
        continue
    preserve.append(('other:' + st.strip(), path))

print('restore:', len(restore), '| preserve:', len(preserve), '| moves:', len(moves))
for kind, p in preserve:
    print('  PRESERVE', kind, p)

# resolve file-move pairs first (r586 law): restore canonical path, then
# verify the untracked stale copy is blob-identical before deleting
for mpath in moves:
    # find where NEW moved it: search NEW tree for the basename
    base = os.path.basename(mpath)
    find = run(['git', 'ls-tree', '-r', '--name-only', NEW]).decode().split()
    cands = [p for p in find if os.path.basename(p) == base]
    assert len(cands) == 1, 'move target ambiguous: %s -> %s' % (mpath, cands)
    tgt = cands[0]
    wtblob = run(['git', 'hash-object', '--', mpath]).decode().strip()
    newblob = run(['git', 'rev-parse', NEW + ':' + tgt]).decode().strip()
    # autocrlf safety: compare blob-space content (LF-normalized)
    r = run(['git', 'show', NEW + ':' + tgt])
    wtraw = open(mpath, 'rb').read()
    same = (r == wtraw) or (r.replace(b'\r\n', b'\n') == wtraw.replace(b'\r\n', b'\n'))
    assert same, 'move pair NOT identical: %s vs %s' % (mpath, tgt)
    if tgt not in restore:
        restore.append(tgt)
    print('  MOVE-PAIR ok:', mpath, '->', tgt, '(identical, stale copy will be deleted)')

if restore:
    run(['git', 'checkout', NEW, '--'] + restore)
    print('restored', len(restore), 'faces from', NEW[:9])
for mpath in moves:
    os.remove(mpath)
    print('deleted stale untracked copy:', mpath)

out2 = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
print('--- post-realign status ---')
print(out2.strip() or '(clean)')
print('behind origin:', run(['git', 'rev-list', '--count', 'HEAD..origin/main']).decode().strip())
