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

# 1. clean merge tree (base 4de45c3e0, zero file intersection pre-verified)
mt = run('git', 'merge-tree', '--write-tree', '--merge-base=4de45c3e0',
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

# 3. payload count assert: diff origin/main..tree == my 19 payload files
p = run('git', 'diff', '--name-only', 'origin/main', tree)
payload = sorted(l for l in p.stdout.splitlines() if l.strip())
expected = 19
assert len(payload) == expected, f'payload count {len(payload)} != {expected}'
print('payload count assert:', len(payload), 'files == expected 19')

# 4. commit-tree on origin/main + push
msg = ('round 566 surgical (merge-tree of 8fdb0c3d6+ad7d84a08 onto origin '
       'f1993725c, zero-intersection clean): W64 same-band double-freeze '
       'YIELD to bm-a (crashed r565 heritage discarded, 10 shards '
       'attribution-verified, zero ledger pollution) + W65 FREEZE (bm-b '
       'TWENTIETH owned, seat MSG-20261002-0919-bmb, ADMIT 64-keys, prereg '
       'W63-anchored head 503,148, W64 in-flight FAIL-CLOSED r307, selftest '
       'W2..W65 PASS) [via bm-b r566]')
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
