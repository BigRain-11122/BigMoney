# r562 bm-a push 1: W53/W54 finalize products + W57 12/12 shards + lane faces
# + r561 adoption (16 untracked tools) + MSG-0700. Surgical diff-based payload
# staging per r523/r530/r531; guards: deletion-set empty (r519), payload count
# exact (r516), json.loads validation with byte-pinned hash-object (race-free),
# post-push delivery ls-tree + other-machine file mirror check (r331).
import subprocess, sys, os, json

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def git(*args, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True,
                       env=env, input=inp)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3], (r.stderr or b'').decode('utf-8', 'replace')[:400]))
    return r.stdout.decode('utf-8', 'replace')

W57_SHARDS = ['results/p2cal_ext/n1_w57/shard-%d-of-12.json' % i for i in range(12)]
R561_ADOPT = sorted(
    'results/' + f for f in os.listdir(os.path.join(REPO, 'results'))
    if f.startswith('_r561bma_'))
R562_TOOLS = [
    'results/_r562bma_push1.py',
    'results/_r562bma_w57_backfill.py',
    'results/_r562bma_w56_s78.txt',
    'results/_r562bma_w57_s78.txt',
]
payload = [
    'results/perpetual_faces/n1_w57_results.json',
    'research/PERPETUAL_N1_W57_PREREG.md',
] + W57_SHARDS + [
    'results/pool_core_samples.jsonl',
    'results/autofill_state.bm-a.json',
    'results/saturation_engine/face_bm-a.json',
    'results/saturation_engine/history_bm-a.jsonl',
    'results/saturation_engine/ledger_bm-a.jsonl',
    'results/saturation_engine/state_bm-a.json',
    'fleet/inbox/MSG-20261002-0700-bm-a.md',
] + R561_ADOPT + R562_TOOLS

MSG = (
    "W57 full-lifecycle same-window closeout: finalize one-pass prev 487,748 "
    "-> 489,948 (K=123,320 == r561 prereg projection bitwise; FAIL-CLOSED "
    "prior-wave file set w2..w56 complete, r307 two-state law) + 12/12 "
    "shards delivered same commit (tick engine burn 06:39..06:50, r310 "
    "completeness gate self-proven) + prereg S7/S8 mechanical backfill "
    "(derive-not-copy, results/_r562bma_w57_backfill.py; 11+/4- = bm-b "
    "_r561bmb_w5356_backfill precedent shape). Same-window yield receipt: "
    "bm-a W53/W54 first-run blocks mathematically identical to origin-"
    "first blocks (bm-c r353 W53 adopted-heritage + bm-b r561 W54->W55-"
    ">W56 chain) -- pre-push r518 guard caught, unpushed blocks deleted "
    "zero-pollution (deterministic three-machine cross-validation), MSG-"
    "0700 rev2; chain now FULLY CAUGHT UP W1..W57, ledger head 489,948, "
    "zero in-flight upstream seats. pool_core_samples.jsonl union ride "
    "(origin 598 rows verbatim + 12 bm-a W57 burn rows, r294 conflict-"
    "region union). r561 crashed-session heritage adoption: 16 untracked "
    "probe/tool files + inbox stale-copy cleanup verified (0615 byte-"
    "identical to origin processed/, 0552/063x stale superseded snapshots "
    "removed). r561 death-cause: S6 PS loop runner & @args2 scalar-string "
    "arg blast (r495 family, all legs zero-exec) -- S6 chain re-run fixed "
    "this round [via bm-a r562]"
)

for attempt in range(3):
    git('fetch', 'origin')
    parent = git('rev-parse', 'origin/main').strip()

    # pre-push sanity: fresh-origin W57 finalize product must NOT exist yet
    # (same-window finalize collision guard, r518)
    for probe in ('results/perpetual_faces/n1_w57_results.json',):
        if git('ls-tree', parent, probe).strip():
            sys.exit('YIELD: %s already on origin (r518 later-arriver law) -- re-derive needed' % probe)

    idx = os.path.join(REPO, '.git', 'idx_r562a')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)

    def gidx(*args, inp=None):
        return git(*args, env=env, inp=inp)

    gidx('read-tree', parent)
    staged = 0
    for p in payload:
        fp = os.path.join(REPO, p)
        if not os.path.exists(fp):
            sys.exit('MISSING PAYLOAD FILE: ' + p)
        data = open(fp, 'rb').read()
        # byte-pinned validation: the blob we stage is exactly the bytes we validate
        if p.endswith('.json'):
            json.loads(data.decode('utf-8'))
        elif p.endswith('.jsonl'):
            for ln in data.decode('utf-8').splitlines():
                if ln.strip():
                    json.loads(ln)
        sha = subprocess.run(['git', '-C', REPO, 'hash-object', '-w', '--stdin'],
                             input=data, capture_output=True).stdout.decode().strip()
        gidx('update-index', '--add', '--cacheinfo', '100644,%s,%s' % (sha, p))
        staged += 1

    diff = [l for l in gidx('diff-index', '--cached', '--name-status', parent).splitlines() if l.strip()]
    names = {l.split('\t', 1)[1] for l in diff}
    dels = [l for l in diff if l.startswith('D')]
    if dels:
        sys.exit('DELETION SET NON-EMPTY (r519 abort): %s' % dels)
    # r343 law: payload files already byte-identical on origin = legitimate
    # already-delivered state, NOT missing -- expected set = differing blobs only
    expected = set()
    for p in payload:
        new_sha = gidx('ls-files', '-s', p).split()[1] if gidx('ls-files', '-s', p).strip() else None
        old_line = git('ls-tree', parent, p).strip()
        old_sha = old_line.split()[2] if old_line else None
        if new_sha != old_sha:
            expected.add(p)
    if names != expected:
        sys.exit('ASSERT FAIL missing=%s extra=%s' % (expected - names, names - expected))
    print('attempt %d: parent=%s staged=%d payload-diff=%d deletion-set=EMPTY' % (attempt, parent[:10], staged, len(expected)))

    tree = gidx('write-tree').strip()
    csha = git('commit-tree', tree, '-p', parent, inp=MSG.encode('utf-8')).strip()
    r = subprocess.run(['git', '-C', REPO, 'push', 'origin', csha + ':main'],
                       capture_output=True)  # r559 law: explicit origin refspec
    if r.returncode == 0:
        print('PUSHED', csha)
        break
    print('push rejected (attempt %d): %s' % (attempt, r.stderr.decode('utf-8', 'replace')[:200]))
else:
    sys.exit('push rejected 3x')

# delivery self-proof (r331): every payload file on fresh origin + mirror
# check that other machines' recent products survived the push
git('fetch', 'origin')
head = git('rev-parse', 'origin/main').strip()
assert head == csha, 'origin/main != pushed sha'
for p in payload:
    assert git('ls-tree', head, p).strip(), 'DELIVERY FAIL: ' + p
mirror = ['results/p2cal_ext/n1_w56/shard-11-of-12.json',
          'results/perpetual_faces/n1_w53_results.json',
          'results/perpetual_faces/n1_w56_results.json',
          'results/p2cal_ext/n1_w54/shard-11-of-12.json']
for p in mirror:
    assert git('ls-tree', head, p).strip(), 'MIRROR FAIL (r331): other-machine file missing: ' + p
print('DELIVERY OK: %d/%d files; mirror check 4/4 (bm-b W54-56 chain + W56 shards intact)' % (len(payload), len(payload)))

# re-anchor: reset --mixed + checkout origin-owned faces EXCEPT live lane faces
git('reset', '--mixed', csha)
KEEP = {'results/autofill_state.bm-a.json', 'results/saturation_engine/state_bm-a.json',
        'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/history_bm-a.jsonl',
        'results/saturation_engine/ledger_bm-a.jsonl', 'results/pool_core_samples.jsonl'}
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
    print('checkout synced %d origin-owned files (live lane faces kept)' % len(paths))
else:
    print('tree clean vs pushed HEAD except live daemon faces')
