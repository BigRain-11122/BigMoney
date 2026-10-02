# r562 bm-a closeout push: S6 chain outputs + S7 products (state/heartbeat/
# round report) + fixed S6 runner + evidence log. Surgical diff-based staging
# (r523/r530/r531). Guards: r519 deletion-set, r343 payload-diff assertion,
# r505 take-new pre-application for shared regen faces with ts field,
# pool_core_samples.jsonl re-union vs fresh origin (r294 conflict-region law).
import subprocess, sys, os, json

REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def git(*args, env=None, inp=None):
    r = subprocess.run(['git', '-C', REPO] + list(args), capture_output=True,
                       env=env, input=inp)
    if r.returncode != 0:
        sys.exit('GIT FAIL %s -> %s' % (args[:3], (r.stderr or b'').decode('utf-8', 'replace')[:400]))
    return r.stdout

def gtxt(*args, **kw):
    return git(*args, **kw).decode('utf-8', 'replace')

NEW_FILES = ['results/_r562bma_s6_runner.py', 'results/_r562bma_s6_chain.log']

MSG = (
    "round 562 closeout (bm-a): W57 full-lifecycle same-window close -- "
    "finalize one-pass head 489,948 (K=123,320 == prereg projection), chain "
    "W1..W57 FULLY CAUGHT UP zero in-flight seats; W53/W54 same-window yield "
    "to origin-first blocks (r518 pre-push guard catch, deterministic "
    "three-machine cross-validation, unpushed duplicates deleted); S6 chain "
    "REPAIRED + re-run 28 legs rc0 (r561 death-cause = PS & @args2 scalar "
    "string blast r495-family -> python subprocess runner; dualrun streak "
    "28/3 zero-drift; scorecard/clock ORANGE_COOL/REPORT+LIVE-2026-10-02/"
    "build_status all refreshed as host=bm-a; holiday 9 live.paper-family "
    "legs honest-skip logged); r561 heritage adoption (16 tools) + inbox "
    "stale-copy cleanup (4 files byte-verified vs origin processed/) + "
    "MSG-0640 processed (cure items 1/2 already landed in r561 W57 freeze "
    "tooling, deletion-set leg live-proven this window); state round_no=562 "
    "(r561 crash-number skipped per r529), heartbeat epoch REWRITTEN with "
    "true UTC int (fixes +8h local-as-UTC face, R170/R178 law); WM=insuffi"
    "cient_history honest + compute_audit pool_starvation flag = post-"
    "catchup honest read (W58 = never-dry next target); CODELY 111KB>50KB "
    "re-archive debt surfaced (in-service pitlaws not archived for byte "
    "count per r514; threshold re-anchor = group/GM decision face) "
    "[via bm-a r562]"
)

for attempt in range(3):
    git('fetch', 'origin')
    parent = gtxt('rev-parse', 'origin/main').strip()
    ob = git('show', 'origin/main:results/pool_core_samples.jsonl')

    # re-union pool samples vs fresh origin (my disk copy may be stale now)
    lb = open(os.path.join(REPO, 'results/pool_core_samples.jsonl'), 'rb').read()
    olines, llines = ob.splitlines(), lb.splitlines()
    oset = set(olines)
    mine = [l for l in llines if l not in oset]
    missing = [l for l in olines if l not in set(llines)]
    if missing:
        out = ob if ob.endswith(b'\n') else ob + b'\n'
        for l in mine:
            out += l + b'\n'
        open(os.path.join(REPO, 'results/pool_core_samples.jsonl'), 'wb').write(out)
        print('pool samples re-union: origin %d + mine %d = %d rows' % (len(olines), len(mine), len(out.splitlines())))
    else:
        print('pool samples: local == origin superset (no re-union needed)')

    # enumerate tracked-modified files
    st = gtxt('status', '--porcelain=v1', '-uno').splitlines()
    mfiles = [l[3:].strip() for l in st if l[0] in 'MA' and l[1] != 'D']
    payload = mfiles + NEW_FILES
    for p in payload:
        if not os.path.exists(os.path.join(REPO, p)):
            sys.exit('MISSING PAYLOAD FILE: ' + p)

    idx = os.path.join(REPO, '.git', 'idx_r562b')
    if os.path.exists(idx):
        os.remove(idx)
    env = dict(os.environ, GIT_INDEX_FILE=idx)

    def gidx(*args, inp=None):
        return git(*args, env=env, inp=inp).decode('utf-8', 'replace')

    gidx('read-tree', parent)
    staged = skipped_new = 0
    for p in payload:
        data = open(os.path.join(REPO, p), 'rb').read()
        # r505 take-new pre-application: shared regen faces with ts field --
        # if fresh origin's ts is newer than disk's, keep origin's (skip)
        old_line = gtxt('ls-tree', parent, p).strip()
        if old_line and p.endswith('.json'):
            try:
                od = json.loads(git('show', '%s:%s' % (parent, p)))
                nd = json.loads(data.decode('utf-8'))
                ots, nts = od.get('ts'), nd.get('ts')
                if isinstance(ots, str) and isinstance(nts, str) and ots > nts:
                    skipped_new += 1
                    continue  # origin face is wall-clock newer -> take-new
            except Exception:
                pass
        if p.endswith('.json'):
            json.loads(data.decode('utf-8'))  # byte-pinned validation
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
    expected = set()
    for p in payload:
        s_line = gidx('ls-files', '-s', p).strip()
        new_sha = s_line.split()[1] if s_line else None
        old_line = gtxt('ls-tree', parent, p).strip()
        old_sha = old_line.split()[2] if old_line else None
        if new_sha and new_sha != old_sha:
            expected.add(p)
    if names != expected:
        sys.exit('ASSERT FAIL missing=%s extra=%s' % (expected - names, names - expected))
    print('attempt %d: parent=%s staged=%d (take-new skip=%d) payload-diff=%d deletion-set=EMPTY' % (
        attempt, parent[:10], staged, skipped_new, len(expected)))

    tree = gidx('write-tree').strip()
    csha = gtxt('commit-tree', tree, '-p', parent, inp=MSG.encode('utf-8')).strip()
    r = subprocess.run(['git', '-C', REPO, 'push', 'origin', csha + ':main'], capture_output=True)
    if r.returncode == 0:
        print('PUSHED', csha)
        break
    print('push rejected (attempt %d): %s' % (attempt, r.stderr.decode('utf-8', 'replace')[:200]))
else:
    sys.exit('push rejected 3x')

# delivery self-proof + behind-count for the round report line
git('fetch', 'origin')
head = gtxt('rev-parse', 'origin/main').strip()
assert head == csha, 'origin/main != pushed sha'
for p in payload:
    if p in expected:
        assert gtxt('ls-tree', head, p).strip(), 'DELIVERY FAIL: ' + p
behind = gtxt('rev-list', '--count', 'HEAD..origin/main').strip()
print('DELIVERY OK: %d/%d differing files on origin/main %s; local-behind=%s' % (
    len(expected), len(expected), head[:10], behind))
