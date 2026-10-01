# -*- coding: utf-8 -*-
# r337 bm-c surgical push: W29 freeze (crashed-r336 half-work adopted & verified
# this round) + bm-c lane files + provenance tools, onto fresh origin/main.
# r523-3 pattern (fresh parent in-script, retry loop, zero deletions r525,
# post-push delivery self-verify r331).
import io, sys, os, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'
BASE = '96d1b5544'   # r336 W26 finalize (last shared point, already on origin)

def git(*a, env=None, check=True):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True, env=env)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.returncode, r.stderr.decode('utf-8', 'replace')[:300])
        sys.exit(1)
    return r

# my commit-set files (base..HEAD) + the two engine lane faces the burn keeps
# rewriting (add picks the freshest working-tree bytes = ride semantics) +
# this round's provenance tools
out = git('diff', '--name-only', BASE + '..HEAD').stdout.decode().strip().splitlines()
FILES = sorted(set(out) | {
    'results/saturation_engine_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json',
    'results/_r337bmc_surgical_push.py',
    'results/_r337bmc_w29_w30_merge.py',
})
print('FILE SET', len(FILES), 'files')

git('fetch', 'origin')
parent = git('rev-parse', 'origin/main').stdout.decode().strip()
print('PARENT', parent[:12])

# origin's recent changes (the commits between my base and origin tip) -- my
# staged set must not silently overwrite any origin-newer file (r531/r516 law)
# EXCEPT the 3 constructively-merged canon/script files (r531 theirs-as-base
# merge verified this round: merged content preserves bm-a r541 W30 rows,
# only deletions vs origin = the stale-pin amendment, +169/-3 self-checked)
MERGED = {'research/PERPETUAL_FACES.md', 'scripts/perpetual_faces.py',
          'scripts/perpetual_faces_n1.py'}
origin_changed = set(git('diff', '--name-only', BASE + '..origin/main').stdout.decode().strip().splitlines())
clash = sorted((set(FILES) & origin_changed) - MERGED)
print('INTERSECTION beyond disclosed merge:', clash if clash else 'EMPTY')
assert not clash, 'stale-base hazard: refusing to overwrite origin-newer files'

tmp_idx = os.path.join(os.environ.get('TEMP', r'C:\Windows\Temp'), 'r337bmc_idx')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)
git('read-tree', parent, env=env)
for f in FILES:
    git('add', '--', f, env=env)
staged = git('diff', '--cached', '--name-only', parent, env=env).stdout.decode().strip().splitlines()
assert sorted(staged) == sorted(FILES), 'staged set mismatch: %s vs %s' % (sorted(staged), sorted(FILES))
# zero-deletion self-proof (r525): staged tree must delete nothing present in parent
dels = git('diff', '--cached', '--name-status', parent, env=env).stdout.decode().strip().splitlines()
assert not [d for d in dels if d.startswith('D')], 'UNEXPECTED DELETIONS: %r' % dels
tree = git('write-tree', env=env).stdout.decode().strip()
print('TREE', tree[:12], 'staged', len(staged), 'files, deletions 0')

MSG = ('r337 W29 freeze delivery (CONSTRUCTIVE MERGE with bm-a r541 W30 landed mid-adoption, '
       'r531 theirs-as-base law): EIGHTEENTH engine wave bm-c sixth-owned (rotation slot '
       'W29=bm-c per W28 row verbatim), A 101_004..103_003 / B 40_651..40_850 BOTH '
       'arithmetic-clean ADMIT receipt _r336bmc_w29_band_gate.py (27-row pre-W29 scan + '
       'N3-R1 leg + probe-cluster r335 leg, no skip R250; W28 W29+ WARNING projection '
       'verified; bands == bm-a W30 published-projection reservation exactly -- r531 '
       'band-disjoint coexistence), prereg PERPETUAL_N1_W29_PREREG.md (prev=live-head '
       'derive, drafting-window W27/W28 pending disclosed and superseded by their landed '
       'finalizes on origin, sec.5 anchors=W26 values), law sec.4 W29 row before W30 row + '
       'WAVE_CONFIGS/N1_BANDS[29] + selftest W29 materializer leg (inserted before W30 leg) + '
       'banned gate ADMIT + n1/pf selftests PASS on MERGED tree (W29+W30 faces both green) + '
       'smoke 47/47; their stale W30 prior-wave pin minimally amended +29 per r531-1 '
       '(their own freeze-window comment projected the auto-join; derive law untouched; '
       'only deletions vs origin = the 2 pin lines, +169/-3 self-checked); crashed-r336 '
       'half-work adopted per r322/r471 after three-face verify; engine ignition observed '
       'same-window (shards burned 22:20+ pre-push per r535 precedent, disclosed); W31+ '
       'handover: W31=bm-b slot per W30 row; + ride lane faces (autofill/dispatcher/'
       'satengine bm-c + pool_dualrun evidence) + provenance tools (merge + surgical scripts)')
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

git('fetch', 'origin')
for f in ('research/PERPETUAL_FACES.md', 'research/PERPETUAL_N1_W29_PREREG.md',
          'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
          'results/_r336bmc_w29_band_gate.py'):
    rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'origin/main:' + f], capture_output=True).returncode
    print('DELIVERED' if rc == 0 else 'MISSING', f)
nxt = git('rev-list', '--count', sha + '..origin/main').stdout.decode().strip()
print('ORIGIN_MOVED_AFTER_ME', nxt)
print('SURGICAL_PUSH_OK', sha)
