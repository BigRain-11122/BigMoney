# r561 W57 freeze surgical push (r523 path, r530 diff-based staging):
# payload = 5 registration faces (prereg + canon + N1_BANDS + WAVE_CONFIGS
# + selftest leg&summary) + r561 tools + clobber-forensics evidence.
# Guards (MSG-0640 cure, all three legs at PUSH time vs FRESH parent):
#   (1) r519 file-level deletion-set empty
#   (2) content-level numstat: zero DELETED lines for the 3 edited tracked
#       files (whole-file staging is blind to content replacement -- this
#       leg catches it)
#   (3) W57 slot vacancy re-verified on FRESH origin post-fetch
import subprocess, sys, os

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def git(*args, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True,
                       env=env, input=inp)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3], r.stderr.decode('utf-8', 'replace')))
    return r.stdout.decode('utf-8', 'replace')

payload = [
    'research/PERPETUAL_N1_W57_PREREG.md',
    'research/PERPETUAL_FACES.md',
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'results/_r561bma_w57_band_gate.py',
    'results/_r561bma_w57_freeze_edits.py',
    'results/_r561bma_s0_surgical.py',
    'results/_r561bma_bugdiff.txt',
    'results/_r561bma_precheck.py',
]
EDITED = {'research/PERPETUAL_FACES.md', 'scripts/perpetual_faces.py',
          'scripts/perpetual_faces_n1.py'}

MSG = (
    "W57 FREEZE one-commit product (never-dry standing step + de-throttle "
    "own-series): FORTY-SIXTH engine wave, bm-a's FOURTEENTH owned, wave 57 "
    "= first free number after the registered W56 row (W56 slot taken "
    "same-window by bm-b r560 -- this machine's W56 drafts yielded unpushed "
    "and unburned, zero pollution, yield_record in round report); BOTH "
    "SIDES ARITHMETIC CONTINUATION no skip (A 157_004..159_003 / B "
    "47_401..47_600, both CLEAN machine-derived == the W56 row W57+ "
    "published projection verbatim -- bm-b r560 freeze gate projection leg "
    "+ this freeze gate cross-validated); ADMIT receipt "
    "results/_r561bma_w57_band_gate.py (leg0 55-keys + leg0b W56-row W57+ "
    "prose + leg1 both-CLEAN + leg2 first-clean==arithmetic + leg3 + "
    "N3-R1 leg + probe-cluster leg + origin slot vacancy machine-checked); "
    "MSG-0640 cure tooling = INSERT-NOT-REPLACE hardening (FIX-A origin "
    "freshness zero-deletions pre-edit + FIX-B last-registered-row anchor "
    "with registered-row survival scan + FIX-C pure-insertion numstat "
    "assert pre-push AND in-push vs fresh parent; summary face = 5th "
    "registration face now explicitly landed); W53/W54/W55/W56 = FOUR "
    "in-flight upstream seats, finalize merge loop FAIL-CLOSED at run "
    "time (r307); prereg anchor=W52 landed K=112,320 head 478,948 + "
    "cumulative pool projection 123,320; banned gate ADMIT; selftest PASS "
    "incl W57 materializer face + summary (n1 PASS full chain + pf 8/8 + "
    "engine 8 legs); W58+ projection A 159_004..161_003 CLEAN / B "
    "47_601..47_800 CLEAN (r561 gate receipt); r561 tools ride (s0 "
    "surgical + freeze edits + precheck + clobber-forensics extract) "
    "[via bm-a r561]"
)

for attempt in range(3):
    git('fetch', 'origin')
    parent = git('rev-parse', 'origin/main').strip()

    # W57 slot vacancy re-verification on FRESH origin (r511 same-window
    # collision guard): if another machine's W57 row landed first ->
    # abort before push = pure yield path.
    opf = git('show', '%s:scripts/perpetual_faces.py' % parent)
    if '57: {"a": (157_004' in opf:
        sys.exit('YIELD: origin/main %s already has a W57 row (same-window '
                 'collision, r511 later-arriver law) -- abort push, zero '
                 'pollution' % parent[:10])
    ocanon = git('show', '%s:research/PERPETUAL_FACES.md' % parent)
    if '- N1 \u6ce257\uff08' in ocanon:
        sys.exit('YIELD: origin canon already has a W57 row -- abort push')

    idx = os.path.join(REPO, '.git', 'idx_r561f')
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

    # MSG-0640 cure leg 1: file-level deletion set must be empty
    diff = [l for l in gidx('diff-index', '--cached', '--name-status', parent).splitlines() if l.strip()]
    names = {l.split('\t', 1)[1] for l in diff}
    dels = [l for l in diff if l.startswith('D')]
    if dels:
        sys.exit('DELETION SET NON-EMPTY (r519 abort): %s' % dels)
    if names != set(payload):
        sys.exit('ASSERT FAIL missing=%s extra=%s' % (set(payload) - names, names - set(payload)))
    # MSG-0640 cure leg 2: content-level -- edited files must show ZERO
    # deleted lines vs the fresh parent (insert-not-replace proof).
    numstat = gidx('diff-index', '--cached', '--numstat', parent)
    for line in numstat.splitlines():
        if not line.strip():
            continue
        add, dele, path = line.split('\t')
        if path in EDITED and int(dele) != 0:
            sys.exit('CONTENT-REPLACE ABORT (MSG-0640 cure): %s shows %s deleted '
                     'lines vs fresh parent -- insert-not-replace violated' % (path, dele))
    print('attempt %d: parent=%s payload=%d files, file-deletions=0, '
          'content-deletions=0 for 3 edited faces' % (attempt, parent[:10], len(payload)))

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
        'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/history_bm-a.jsonl',
        'results/saturation_engine/ledger_bm-a.jsonl', 'results/pool_core_samples.jsonl']
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
