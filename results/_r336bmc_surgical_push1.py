# -*- coding: utf-8 -*-
# r336 bm-c: surgical push #1 -- W26 finalize deliverables onto origin tip.
# r523-3 law: parent rev-parse'd fresh inside script; retry loop cheap (blob unchanged).
# r505 law: intersection pre-check (prereg blob vs origin, product/tools absent check).
# r331 law: post-write ls-tree verification leg (delivery self-verify).
import io, sys, os, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
FILES = [
    'research/PERPETUAL_N1_W26_PREREG.md',
    'results/perpetual_faces/n1_w26_results.json',
    'results/_r336bmc_d19.py',
    'results/_r336bmc_s6_runner.ps1',
    'results/_r336bmc_w26_backfill.py',
    'results/_r336bmc_w26_probe.py',
    'results/_r336bmc_kchain_check.py',
    'results/_r336bmc_anchor_check.py',
]

def git(*a, env=None, check=True):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True, env=env)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.returncode, r.stderr.decode('utf-8', 'replace')[:400])
        sys.exit(1)
    return r

# 1. fresh fetch + parent
git('fetch', 'origin')
parent = git('rev-parse', 'origin/main').stdout.decode().strip()
print('PARENT', parent)

# 2. r505 intersection pre-check
p_local = git('rev-parse', 'HEAD:research/PERPETUAL_N1_W26_PREREG.md').stdout.decode().strip()
p_origin = git('rev-parse', 'origin/main:research/PERPETUAL_N1_W26_PREREG.md').stdout.decode().strip()
print('PREREG_BLOB local=%s origin=%s same=%s' % (p_local[:12], p_origin[:12], p_local == p_origin))
assert p_local == p_origin, 'prereg touched by peer since r335 freeze -- ABORT (r331 overwrite hazard)'
for f in FILES[1:]:
    rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'origin/main:' + f], capture_output=True).returncode
    assert rc != 0, 'origin already has %s -- ABORT' % f
print('INTERSECTION zero -- safe')

# 3. temp-index tree build on origin tip
tmp_idx = os.path.join(os.environ.get('TEMP', r'C:\Windows\Temp'), 'r336bmc_idx')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)
git('read-tree', parent, env=env)
for f in FILES:
    git('add', '--', f, env=env)
staged = git('diff', '--cached', '--name-only', parent, env=env).stdout.decode().strip().splitlines()
assert sorted(staged) == sorted(FILES), 'staged set mismatch: %s' % staged
tree = git('write-tree', env=env).stdout.decode().strip()
print('TREE', tree, 'staged', len(staged), 'files')

# 4. commit-tree + push with retry
MSG = ('r336 W26 finalize: FIFTEENTH engine wave bm-c fifth-owned closeout, ledger 419,548+2,200=421,748 chain-linear '
       '(K=55,120 [canon 120 + W1..W25 52,920 + 2,200; sec.0 drafting-window slip 50,720 disclosed], merged mu -0.09192 '
       'sigma 0.24472 se_mu 0.001042 tightened from W25 0.001063, S5 4/4 PASS [mu-drift +0.00117<0.02 / sigma +0.09%<10% / '
       'A p95 0.3273 vs 0.3054 delta +0.0219<0.05 / K-lift +0.0011<=0.02 @n_eff_held 419,548, canon_flip NOT performed] '
       '-- all four anchors independently re-verified this round against W23/W25 products on origin (bit-exact); '
       'prev_total 419,548 = W25-on-origin derive bit-exact (r322 dangling-claim law, no re-run of finalize per r538 '
       'double-count law -- crashed-session product adopted after three-face verify); prereg sec.7/8 mechanical backfill '
       'same-window + post-backfill n1 selftest default-wave green (r307 two-state) + smoke 47/47 + D-19 MATCH-unchanged; '
       'shards 12/12 on origin (r310 completeness gate, engine append 6a30acf8d self-healed the 5 orphan shards); '
       'CHAIN GATE RELEASED: bm-a W27 finalize (prev=421,748 derive) + bm-b W28 anchor line unblocked; '
       'crashed r336 attempt adopted per r322/r471 (probe/backfill/d19/s6-runner tools included as provenance)')
sha = None
for attempt in range(4):
    if attempt > 0:
        git('fetch', 'origin')
        parent = git('rev-parse', 'origin/main').stdout.decode().strip()
        print('RETRY with new parent', parent[:12])
    sha = git('commit-tree', tree, '-p', parent, '-m', MSG).stdout.decode().strip()
    pr = subprocess.run(['git', '-C', R, 'push', 'origin', sha + ':refs/heads/main'], capture_output=True)
    if pr.returncode == 0:
        print('PUSHED', sha)
        break
    print('push rejected:', pr.stderr.decode('utf-8', 'replace')[:200])
else:
    print('PUSH FAILED after retries')
    sys.exit(1)

# 5. r331 post-write delivery verification
git('fetch', 'origin')
head = git('rev-parse', 'origin/main').stdout.decode().strip()
assert head == sha or git('merge-base', '--is-ancestor', sha, 'origin/main').returncode == 0
for f in FILES:
    rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'origin/main:' + f], capture_output=True).returncode
    print('DELIVERED' if rc == 0 else 'MISSING', f)
nxt = git('rev-list', '--count', sha + '..origin/main').stdout.decode().strip()
print('ORIGIN_MOVED_AFTER_ME', nxt)
print('SURGICAL_PUSH_OK', sha)
