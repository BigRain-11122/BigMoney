"""r637 bm-a: local ff-sync via r589 撤-FF-重落 (reset --mixed + targeted face checkout).
Checkout set = exactly (old-HEAD..origin/main) changed paths -- runtime dirty faces NOT in
that set stay untouched (daemon churn preserved). r608: complete before next daemon tick.
"""
import subprocess, os, sys, hashlib

OLD = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()

# artifact: local untracked duplicate of origin blob (verified byte-identical) -> remove
p = 'results/mass_trial/w2_judge_shard_3of4.jsonl'
if os.path.exists(p):
    h = hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]
    o = subprocess.run(['git', 'show', 'origin/main:' + p], capture_output=True)
    oh = hashlib.sha256(o.stdout).hexdigest()[:16]
    assert h == oh, 'artifact no longer identical?! %s vs %s' % (h, oh)
    os.remove(p)
    print('untracked duplicate removed (sha %s == origin)' % h)

r = subprocess.run(['git', 'reset', '--mixed', 'origin/main'], capture_output=True, text=True)
assert r.returncode == 0, r.stderr
print('reset --mixed ->', subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip())

chg = subprocess.run(['git', 'diff', '--name-only', OLD, 'origin/main'],
                     capture_output=True, text=True).stdout.split()
print('changed paths:', len(chg))
co = subprocess.run(['git', 'checkout', '--'] + chg, capture_output=True, text=True)
assert co.returncode == 0, co.stderr
print('checkout done')

st = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True).stdout
print('--- status after sync ---')
print(st)
