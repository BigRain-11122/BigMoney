# -*- coding: utf-8 -*-
"""r589 bm-a local realign after surgical push (r578 law): update-ref ->
reset --mixed -> face-classified checkout. Live-write faces (engine state)
are PRESERVED in the worktree; stale faces (worktree == old-base blob) are
restored from the new HEAD."""
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO)
NEW = 'ff0b1869b141c06cf6bf226df3f37e9a2ff91762'
OLD = '1699ff61e'   # my pre-surgical local commit (old base for the worktree)

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True)
    if check and r.returncode != 0:
        sys.exit('FAIL %s\n%s' % (cmd[:4], r.stderr.decode('utf-8', 'replace')[-400:]))
    return r.stdout

# 1. move the ref (HEAD symbolic -> main follows)
run(['git', 'update-ref', 'refs/heads/main', NEW])
# 2. re-anchor index (r578: checkout alone is a no-op on "Already on")
run(['git', 'reset', '--mixed', NEW])
print('ref moved + index re-anchored to', NEW[:9])

# 3. classify faces from status (python argv path ops per r580 law)
out = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
stale, livewrite = [], []
for line in out.splitlines():
    st, path = line[:2], line[3:].strip().strip('"')
    if st.strip() == '' or not path:
        continue
    if st.endswith('D'):
        stale.append(path)          # worktree file missing -> restore
        continue
    # M face: compare worktree blob vs OLD-base blob
    wt = run(['git', 'hash-object', '--', path], check=False)
    ob = run(['git', 'rev-parse', OLD + ':' + path], check=False)
    if wt and ob and wt.decode().strip() == ob.decode().strip():
        stale.append(path)          # untouched-by-me stale copy of old base
    else:
        livewrite.append(path)      # actively written (engine ticks) -> preserve
print('stale faces:', len(stale), '| live-write preserved:', len(livewrite))
for p in livewrite:
    print('  PRESERVE:', p)
if stale:
    run(['git', 'checkout', '--'] + stale)
    print('stale faces restored from', NEW[:9])

# 4. verify
out2 = run(['git', 'status', '--porcelain']).decode('utf-8', 'replace')
print('--- post-realign status ---')
print(out2.strip())
head = run(['git', 'rev-parse', 'HEAD']).decode().strip()
origin = run(['git', 'rev-parse', 'origin/main']).decode().strip()
print('HEAD == origin/main:', head == origin, '| behind:', run(['git', 'rev-list', '--count', 'HEAD..origin/main']).decode().strip())
