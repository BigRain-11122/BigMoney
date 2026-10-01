# r559 S0 surgical delivery (r523 path, r530 diff-based staging law):
# adopt r558 crashed-session heritage (W52 yield receipt MSG + 9 evidence tools)
# + bm-a lane/host faces ride; shared regen faces (compute_audit/regime_state/
# update_status .json) left to origin side per r505 take-new (bm-c r351 wrote 05:5x
# > our r558-era 05:3x).
# Laws applied: r531 parent-in-script rev-parse; r343 --cached diff-index assertions;
# r519 deletion-set empty; r341 rejection->rebuild-retry (blobs unchanged).
import subprocess, sys, os, io

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def git(*args, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True,
                       env=env, input=inp)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8', 'replace')

lane = [
    'results/autofill_state.bm-a.json',
    'results/compute_audit.bm-a.json',
    'results/pool_dualrun.bm-a.jsonl',
    'results/regime_state.bm-a.json',
    'results/saturation_engine/face_bm-a.json',
    'results/saturation_engine/history_bm-a.jsonl',
    'results/saturation_engine/state_bm-a.json',
    'results/scorecard_v1.json',
    'results/strategy_scorecard.json',
    'results/update_status.bm-a.json',
]
heritage = [
    'fleet/inbox/MSG-20261002-0615-bm-a.md',
    'results/_r558bma_cas_push.py',
    'results/_r558bma_extract.py',
    'results/_r558bma_extract2.py',
    'results/_r558bma_extract3.py',
    'results/_r558bma_s0_surgical.py',
    'results/_r558bma_union_repair.py',
    'results/_r558bma_w48_backfill.py',
    'results/_r558bma_w52_band_gate.py',
    'results/_r558bma_w52_freeze_edits.py',
]
payload = lane + heritage

MSG = (
    "r559 S0 heritage adoption + lane ride: adopt crashed r558 session heritage -- "
    "W52 same-window yield receipt MSG (content + r559 addendum: W53 seat since taken by "
    "bm-c 8d09d27c3, bm-a next own target W54) + 9 r558 evidence tools (_r558bma_* incl "
    "w52_band_gate/w52_freeze_edits yield receipts + s0/union-repair tools referenced by "
    "4c7e3ca0f -- dangling-origin-reference closure per r322) + bm-a engine lane faces + "
    "host faces (scorecard_v1/strategy_scorecard host=bm-a); shared regen faces "
    "(compute_audit/regime_state/update_status) left to origin side per r505 take-new "
    "[via bm-a r559]"
)

for attempt in range(3):
    git('fetch', 'origin')
    parent = git('rev-parse', 'origin/main').strip()
    idx = os.path.join(REPO, '.git', 'idx_r559')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)

    def gidx(*args, inp=None):
        return git(*args, env=env, inp=inp)

    gidx('read-tree', parent)
    staged = 0
    for p in payload:
        if not os.path.exists(os.path.join(REPO, p)):
            sys.exit('MISSING PAYLOAD FILE: ' + p)
        sha = git('hash-object', '-w', p).strip()
        gidx('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (sha, p))
        staged += 1

    # r343 dual-state expectation: payloads already byte-identical on origin
    # (crashed-session self-delivery scenario) = legal delivered state, not missing.
    expected_new = set()
    for p in payload:
        mine = git('hash-object', p).strip()
        remote = git('ls-tree', parent, p).strip()
        rsha = remote.split('\t')[0].split()[2] if remote else None
        if rsha is None or rsha != mine:
            expected_new.add(p)
    # assertions (r343: --cached + line split; r519: deletion set must be empty)
    diff = [l for l in gidx('diff-index', '--cached', '--name-status', parent).splitlines() if l.strip()]
    names = {l.split('\t', 1)[1] for l in diff}
    dels = [l for l in diff if l.startswith('D')]
    if dels:
        sys.exit('DELETION SET NON-EMPTY (r519 abort): %s' % dels)
    if names != expected_new:
        missing = expected_new - names
        extra = names - expected_new
        sys.exit('ASSERT FAIL missing=%s extra=%s' % (missing, extra))
    already = len(payload) - len(expected_new)
    print('attempt %d: parent=%s staged=%d (new=%d already-delivered=%d) deletions=0'
          % (attempt, parent[:10], staged, len(expected_new), already))

    tree = gidx('write-tree').strip()
    csha = git('commit-tree', tree, '-p', parent, inp=MSG.encode('utf-8')).strip()
    r = subprocess.run(['git', '-C', REPO, 'push', 'origin', csha + ':main'], capture_output=True)
    if r.returncode == 0:
        print('PUSHED', csha)
        break
    print('push rejected (attempt %d): %s -- rebuild on fresh parent' % (attempt, r.stderr.decode('utf-8', 'replace')[:200]))
else:
    sys.exit('push rejected 3x')

# post-push delivery self-proof (r531 mirror): ls-tree counterpart presence
git('fetch', 'origin')
head = git('rev-parse', 'origin/main').strip()
assert head == csha, 'origin/main != pushed sha: %s vs %s' % (head, csha)
for p in payload:
    out = git('ls-tree', head, p).strip()
    assert out, 'DELIVERY FAIL (not on origin): ' + p
print('DELIVERY OK: %d/%d payload files on origin/main %s' % (len(payload), len(payload), head[:10]))

# re-anchor local main (reset --mixed, r523) and restore the 3 shared faces to origin side
git('reset', '--mixed', csha)
for p in ['results/compute_audit.json', 'results/regime_state.json', 'results/update_status.json']:
    git('checkout', '--', p)
print('local main re-anchored at', csha[:10])
