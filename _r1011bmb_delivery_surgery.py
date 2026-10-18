# r1011 bm-b delivery surgery: replay r1010 deferred payload (632a256486 + d8bc4f4891) onto fresh origin tip.
# Pattern: r997/r1005/r1008 own-face surgery push (temp-index, commit-tree, CAS hard checks). ASCII only.
import json, os, re, subprocess, sys

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(REPO)

def git(args, env_extra=None, inp=None, timeout=120):
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    try:
        r = subprocess.run(['git'] + args, capture_output=True, text=True,
                            encoding='utf-8', errors='replace', env=env, input=inp, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, '', 'TIMEOUT after %ss' % timeout, 'TIMEOUT after %ss' % timeout
    so = r.stdout or ''
    se = r.stderr or ''
    return r.returncode, so.strip(), se.strip(), so + se

def die(msg):
    print('FATAL: ' + msg)
    sys.exit(2)

HEX = re.compile(r'^[0-9a-f]{40}$')

BASE = 'e326344c93f8ba0d77006c20e2f40f0496146bf1'
MYSRC = 'd8bc4f4891'

OWN = [
    '_r1010bmb_closeout.py',
    '_r1010bmb_s6chain.ps1',
    'fleet/machines/bm-b.json',
    'logs/iteration-loop/round_reports.md',
    'research/HANDOVER.md',
    'results/_orphan_face_probe.bm-b.json',
    'results/_r1010bmb_closeout_receipt.json',
    'results/_r1010bmb_s6_log.txt',
    'results/astock_daily_update_status.json',
    'results/compute_audit.bm-b.json',
    'results/etf_daily_pull_status.json',
    'results/futures_update_status.bm-b.json',
    'results/lhb_update_status.bm-b.json',
    'results/pool_dualrun.bm-b.jsonl',
    'results/regime_state.bm-b.json',
    'results/token_usage.bm-b.json',
    'results/update_status.bm-b.json',
    'state.json',
]

# 0. reflog guard: local main must be exactly my own 2-commit delta over BASE
rc, cur, err, _ = git(['rev-parse', 'main'])
if rc != 0 or not cur.startswith(MYSRC):
    die('local main is %s (rc=%s) expected %s' % (cur, rc, MYSRC))
rc, cnt, err, _ = git(['rev-list', '--count', BASE + '..main'])
if rc != 0 or cnt.strip() != '2':
    die('local ahead-of-base count=%s expected 2' % cnt)
rc, subs, err, _ = git(['log', '--format=%s', BASE + '..main'])
if 'round 1010' not in subs:
    die('foreign commit in local delta: ' + subs[:300])

# 1. fresh fetch + base currency
rc, so, se, _ = git(['fetch', 'origin'], timeout=180)
if rc != 0:
    die('fetch failed rc=%s: %s' % (rc, (so + ' ' + se)[:300]))
rc, tip, err, _ = git(['rev-parse', 'origin/main'])
if tip != BASE:
    die('origin moved to %s mid-flight - rerun surgery with new BASE' % tip)
print('BASE-OK', tip)

# 2. per-face mode+sha from MYSRC (r1008 CAS 40-hex hard checks)
lsinfo = {}
rc, out, err, _ = git(['ls-tree', MYSRC, '--'] + OWN)
if rc != 0:
    die('ls-tree failed: ' + err[:300])
for line in out.splitlines():
    meta, path = line.split('\t', 1)
    mode, typ, sha = meta.split()
    if not HEX.match(sha):
        die('bad sha for ' + path)
    lsinfo[path] = (mode, sha)
missing = [f for f in OWN if f not in lsinfo]
if missing:
    die('missing faces in MYSRC: %s' % missing)

# 3. temp index: read-tree BASE, overlay own faces
IDX = os.path.join(REPO, '.git', '_r1011bmb_tmpidx')
if os.path.exists(IDX):
    os.remove(IDX)
env_idx = {'GIT_INDEX_FILE': IDX}
rc, so, se, _ = git(['read-tree', BASE], env_extra=env_idx)
if rc != 0:
    die('read-tree failed: ' + se[:300])
for f in OWN:
    mode, sha = lsinfo[f]
    rc, so, se, _ = git(['update-index', '--add', '--cacheinfo', '%s,%s,%s' % (mode, sha, f)], env_extra=env_idx)
    if rc != 0:
        die('update-index failed for %s: %s' % (f, se[:200]))

# 4. token_usage.json per-machine union: origin rows for others, -bm-b row mine (r1008 law)
rc, oj, err, _ = git(['show', BASE + ':results/token_usage.json'])
if rc != 0:
    die('origin token face read failed: ' + err[:200])
rc, mj, err, _ = git(['show', MYSRC + ':results/token_usage.json'])
if rc != 0:
    die('mine token face read failed: ' + err[:200])
try:
    O, M = json.loads(oj), json.loads(mj)
except Exception as e:
    die('token json parse: %s' % e)
if isinstance(M.get('machines'), dict) and '-bm-b' in M['machines']:
    O.setdefault('machines', {})['-bm-b'] = M['machines']['-bm-b']
    print('TOKEN-UNION: -bm-b row <- mine, %d machine keys kept from origin' % len(O['machines']))
blob = json.dumps(O, indent=2, ensure_ascii=False) + '\n'
r = subprocess.run(['git', 'hash-object', '-w', '--stdin'], input=blob, capture_output=True,
                   text=True, encoding='utf-8', errors='replace')
tsha = (r.stdout or '').strip()
if r.returncode != 0 or not HEX.match(tsha):
    die('token hash-object failed: ' + (r.stderr or '')[:200])
rc, so, se, _ = git(['update-index', '--add', '--cacheinfo', '100644,%s,results/token_usage.json' % tsha], env_extra=env_idx)
if rc != 0:
    die('token update-index failed: ' + se[:200])

# 5. write-tree
rc, tree, se, _ = git(['write-tree'], env_extra=env_idx)
if rc != 0 or not HEX.match(tree or ''):
    die('write-tree bad: rc=%s out=%s err=%s' % (rc, tree, se[:200]))
print('TREE', tree)

# 6. content-level delivery assertion (r982 law): every own face in tree == MYSRC blob
for f in OWN:
    rc, a, _, _ = git(['rev-parse', tree + ':' + f])
    rc2, b, _, _ = git(['rev-parse', MYSRC + ':' + f])
    if rc != 0 or rc2 != 0 or a != b:
        die('delivery assert fail %s (%s vs %s)' % (f, a, b))
print('DELIVERY-ASSERT 18/18 OK')

# 7. commit-tree on BASE
msg = ('round 1010 delivery replayed on fresh tip f10ecc00e8 (deferred from r1010 night push-hang window, '
       'r1005/r1008 surgery pattern): S6 43 rc0 + D-19 multi-advance zero BigMoney dispatch + content-lane '
       'dispatches registered (CONTENT-LOOP P1 <=10-20, voice lane P1 <=10-22) + 5x HANDOVER stamp; 23 shared '
       'regen faces resolved origin-newer-wins (bm-c 21:22 / bm-a 20:39 > mine 20:26), token_usage per-machine '
       'union (-bm-b row mine, others origin); zero deletions; two local commits superseded, reflog recoverable.')
with open('_r1011bmb_commitmsg.txt', 'w', encoding='utf-8') as fh:
    fh.write(msg)
rc, newc, se, _ = git(['commit-tree', tree, '-p', BASE, '-F', '_r1011bmb_commitmsg.txt'])
if rc != 0 or not HEX.match(newc or ''):
    die('commit-tree bad: rc=%s out=%s err=%s' % (rc, newc, se[:300]))
print('NEWCOMMIT', newc)

# 8. push with timeout guard (night promisor window family)
rc, so, se, out = git(['push', 'origin', newc + ':refs/heads/main'], timeout=220)
low = ((so or '') + '\n' + (se or '')).lower()
if rc == 124:
    print('PUSH-TIMEOUT: delivery deferred again (honest), local surgery commit kept: ' + newc)
    print('ACTION: retry push next window; do NOT update-ref yet (base may move)')
    sys.exit(5)
if rc != 0 or any(w in low for w in ['fatal', 'rejected', 'failed', '! [rejected', 'error:']):
    print('PUSH-REJECTED rc=%s' % rc)
    print(out[:1500])
    sys.exit(3)
print('PUSH-OK')

# 9. positive delivery verification: fetch + rev-parse + ls-tree spot checks
rc, so, se, _ = git(['fetch', 'origin'], timeout=120)
rc, tip2, err, _ = git(['rev-parse', 'origin/main'])
if tip2 != newc:
    print('DELIVERY-UNVERIFIED tip=%s expected=%s' % (tip2, newc))
    sys.exit(4)
rc, spot, _, _ = git(['ls-tree', 'origin/main', '--', 'state.json', 'fleet/machines/bm-b.json',
                      'logs/iteration-loop/round_reports.md', 'results/token_usage.json'])
ok = ('state.json' in spot and 'bm-b.json' in spot and 'round_reports.md' in spot and 'token_usage.json' in spot)
print('LS-TREE-SPOT', 'OK' if ok else spot[:300])

# 10. move local main (reflog guard passed at step 0) + reset --mixed (worktree untouched)
rc, so, se, _ = git(['update-ref', 'main', newc])
if rc != 0:
    die('update-ref failed: ' + se[:200])
rc, so, se, _ = git(['reset', '--mixed', 'main'])
if rc != 0:
    die('reset failed: ' + se[:200])
rc, head, _, _ = git(['rev-parse', 'main'])
rc, behind, _, _ = git(['rev-list', '--count', 'main..origin/main'])
rc, ahead, _, _ = git(['rev-list', '--count', 'origin/main..main'])
print('LOCAL-MAIN', head, 'behind=' + behind, 'ahead=' + ahead)
if os.path.exists(IDX):
    os.remove(IDX)
print('SURGERY-DELIVERY-COMPLETE')
