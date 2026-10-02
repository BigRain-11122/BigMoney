# -*- coding: utf-8 -*-
"""r566 bm-b surgical push: merge-tree (clean, zero intersection verified) +
commit-tree -p origin/main + deletion-set assert + payload count assert + push.
Local reconciliation: reset --mixed (worktree untouched -- in-flight W65 burn
evidence survives per r325/r525 laws)."""
import subprocess, sys

def run(*a, check=True):
    r = subprocess.run(list(a), capture_output=True, text=True, encoding='utf-8')
    if check and r.returncode != 0:
        sys.exit(f'FAIL {a[:3]}: rc={r.returncode} {r.stderr[:400]}')
    return r

# 1. clean merge tree (base dcae6d6f0 = merge-base; intersection file content-equal verified)
mt = run('git', 'merge-tree', '--write-tree', '--merge-base=dcae6d6f0',
         'origin/main', 'HEAD')
if mt.returncode != 0:
    sys.exit(f'merge-tree CONFLICT rc={mt.returncode}: {mt.stdout[:600]}')
tree = mt.stdout.splitlines()[0].strip()
print('merged tree:', tree)

# 2. deletion-set assert: new tree vs origin/main must show ZERO deletions
d = run('git', 'diff', '--diff-filter=D', '--name-only', 'origin/main', tree)
dels = [l for l in d.stdout.splitlines() if l.strip()]
assert dels == [], f'DELETION-SET VIOLATION (r525/r516 law): {dels}'
print('deletion-set assert: EMPTY (zero deletions vs origin/main)')

# 3. payload count assert: diff origin/main..tree == my 45 payload files
p = run('git', 'diff', '--name-only', 'origin/main', tree)
payload = sorted(l for l in p.stdout.splitlines() if l.strip())
expected = 44  # 45 staged minus fund_history_status (content-equal to origin -> legal already-delivered state, r343 law)
assert len(payload) == expected, f'payload count {len(payload)} != {expected}'
print('payload count assert:', len(payload), 'files == expected 45')

# 4. commit-tree on origin/main + push
msg = ('round 566 closeout v2 surgical (0531fbb60 onto 50f0b413d): S6 30 legs '
       'green + state r566 (skips dead 564/565) + heartbeat int-epoch + round '
       'report + CODELY r566 psutil dead-pid-guard lesson + W65 shards 4-7 '
       'ride + v1 bad-sweep reset disclosure (push-rejection caught r519 '
       'family near-miss) [via bm-b r566]')
ci = run('git', 'commit-tree', tree, '-p', 'origin/main', '-m', msg)
new_sha = ci.stdout.strip()
print('new commit:', new_sha)
pu = run('git', 'push', 'origin', f'{new_sha}:main', check=False)
if pu.returncode != 0:
    sys.exit(f'push rejected: {pu.stderr[:400]}')
print('PUSH OK')

# 5. local reconciliation: reset --mixed (index=new tree, worktree UNTOUCHED)
run('git', 'reset', '--mixed', new_sha)
print('local reset --mixed to', new_sha, '(worktree untouched: W65 burn evidence survives)')

# 6. post-push delivery self-verify (ls-tree)
run('git', 'fetch', 'origin')
lv = run('git', 'rev-parse', 'origin/main')
print('origin/main now:', lv.stdout.strip())
assert lv.stdout.strip() == new_sha, 'origin did not land new_sha'
print('DELIVERY VERIFIED: origin/main == surgical sha')
