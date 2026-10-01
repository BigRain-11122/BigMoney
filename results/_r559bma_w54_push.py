# r559 W54 freeze surgical push (r523 path, r530 diff-based staging):
# payload = 4 canonical freeze files + prereg + 4 r559 tools.
# Guards: r519 deletion-set empty; r343 payload count; W54 slot vacancy
# re-verified on FRESH origin post-fetch (same-window collision with
# bm-b's declared W54 target -> abort = yield per r511, zero pollution).
import subprocess, sys, os

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def git(*args, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True,
                       env=env, input=inp)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8', 'replace')

payload = [
    'research/PERPETUAL_N1_W54_PREREG.md',
    'research/PERPETUAL_FACES.md',
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'results/_r559bma_w54_band_gate.py',
    'results/_r559bma_w54_freeze_edits.py',
    'results/_r559bma_s0_surgical.py',
    'results/_r559bma_bulk_checkout.py',
]

MSG = (
    "W54 FREEZE one-commit product (never-dry standing step + de-throttle "
    "own-series): FORTY-THIRD engine wave, bm-a's THIRTEENTH owned, wave 54 = "
    "first free number after the registered W53 row (bm-a's previous W48 "
    "closed full-lifecycle at r558 seat-loss re-derive K=103,520); BOTH "
    "SIDES ARITHMETIC CONTINUATION no skip (A 151_004..153_003 / B "
    "46_601..46_800, both CLEAN machine-derived == the W53 row W54+ "
    "published projection verbatim -- three-machine cross-validation: "
    "bm-c r351 freeze gate + bm-b r559 yield-window gate + this freeze "
    "gate); ADMIT receipt results/_r559bma_w54_band_gate.py (leg0 52-keys "
    "+ leg0b prose + leg1 both-CLEAN + leg2 first-clean==arithmetic + leg3 "
    "+ N3-R1 leg + probe-cluster leg + origin slot vacancy "
    "machine-checked); W53 bm-c in-flight finalize coexists by band "
    "disjointness (r531) -- ONE in-flight upstream seat, finalize merge "
    "loop FAIL-CLOSED at run time (r307); prereg anchor=W52 landed "
    "K=112,320 head 478,948 + cumulative pool projection 116,720; banned "
    "gate ADMIT; selftest PASS incl W54 materializer face + summary "
    "(n1 PASS + pf 8/8 + engine 8 legs); W55+ projection A "
    "153_004..155_003 CLEAN / B 46_801..47_000 REFUSED at SEED_REGISTRY "
    "value 47_000 (skip family at W55); r559 tools ride (s0 surgical + "
    "bulk checkout + freeze edits) [via bm-a r559]"
)

for attempt in range(3):
    git('fetch', 'origin')
    parent = git('rev-parse', 'origin/main').strip()

    # W54 slot vacancy re-verification on FRESH origin (r511 same-window
    # collision guard): if another machine's W54 row landed first ->
    # abort before push = pure yield path.
    opf = git('show', '%s:scripts/perpetual_faces.py' % parent)
    if '54: {"a"' in opf:
        sys.exit('YIELD: origin/main %s already has a W54 row (same-window '
                 'collision, r511 later-arriver law) -- abort push, zero '
                 'pollution' % parent[:10])
    ocanon = git('show', '%s:research/PERPETUAL_FACES.md' % parent)
    if '- N1 \u6ce254' in ocanon:
        sys.exit('YIELD: origin canon already has a W54 row -- abort push')

    idx = os.path.join(REPO, '.git', 'idx_r559f')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)

    def gidx(*args, inp=None):
        return git(*args, env=env, inp=inp)

    gidx('read-tree', parent)
    for p in payload:
        if not os.path.exists(os.path.join(REPO, p)):
            sys.exit('MISSING PAYLOAD FILE: ' + p)
        sha = git('hash-object', '-w', p).strip()
        gidx('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (sha, p))

    diff = [l for l in gidx('diff-index', '--cached', '--name-status', parent).splitlines() if l.strip()]
    names = {l.split('\t', 1)[1] for l in diff}
    dels = [l for l in diff if l.startswith('D')]
    if dels:
        sys.exit('DELETION SET NON-EMPTY (r519 abort): %s' % dels)
    if names != set(payload):
        sys.exit('ASSERT FAIL missing=%s extra=%s' % (set(payload) - names, names - set(payload)))
    print('attempt %d: parent=%s payload=%d files, deletions=0' % (attempt, parent[:10], len(payload)))

    tree = gidx('write-tree').strip()
    csha = git('commit-tree', tree, '-p', parent, inp=MSG.encode('utf-8')).strip()
    r = subprocess.run(['git', '-C', REPO, 'push', 'origin', csha + ':main'], capture_output=True)
    if r.returncode == 0:
        print('PUSHED', csha)
        break
    print('push rejected (attempt %d): %s -- rebuild on fresh parent' % (attempt, r.stderr.decode('utf-8', 'replace')[:200]))
else:
    sys.exit('push rejected 3x')

# delivery self-proof + re-anchor + checkout origin-owned faces
git('fetch', 'origin')
head = git('rev-parse', 'origin/main').strip()
assert head == csha, 'origin/main != pushed sha'
for p in payload:
    assert git('ls-tree', head, p).strip(), 'DELIVERY FAIL: ' + p
print('DELIVERY OK: %d/%d files on origin/main %s' % (len(payload), len(payload), head[:10]))
git('reset', '--mixed', csha)
KEEP = ['results/autofill_state.bm-a.json', 'results/saturation_engine/state_bm-a.json',
        'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/history_bm-a.jsonl']
out = subprocess.check_output(['git', '-C', REPO, 'status', '--porcelain'], text=True)
paths = []
for line in out.splitlines():
    st = line[:2]
    if st == '??':
        continue
    p = line[3:].strip()
    if p in KEEP:
        continue
    paths.append(p)
if paths:
    git('checkout', '--', *paths)
    print('checkout synced %d origin-owned files' % len(paths))
else:
    print('tree clean vs HEAD except live daemon faces')
