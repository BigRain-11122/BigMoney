# r1084-continuation bm-c: LEDGER receipt row CAS surgical push to group-tree origin/main
# Law: CEO 2026-10-18 00:2x memory-governance four-piece, receipt = cph4/fleet/memory-slim/LEDGER.md bm-c row.
# Method: temp-index surgical commit (zero working-tree touch; group tree is dirty [ahead3/behind12+2 daemon live-writes]).
# CAS loop: parent = current origin/main at push time; non-FF push = refetch + re-append + retry (max 3).
import subprocess
import sys

REPO = 'K:/Fluxgroup/FluxGroup'
PATH = 'cph4/fleet/memory-slim/LEDGER.md'

ROW = ('| 2026-10-18 | 377,015→97,121（gate v2 首跑执行·220 条 verbatim 迁 9 主题文件·快照 cleanup-gate-2026-10-18）→87,547（bm-c 身份元组注 User 首位[死窗 07:59 piece-3]+术后跨机污染清扫 10 条迁隔离档+1 条 CEO 云端恢复律 SIGS 误伤回迁） '
       '| 324→104→95 | bm-c 四件全执行收口（①agent-library-sync 幂等确认 24/24 在位 ②gate v2 首跑 ③L0 身份元组+跨机污染清扫[含 08:06:35 REPLACE-DOWN 回灌事故实锚：死窗 07:59 术后被 worker poke 联合重建重胀回 377,015B→本窗 fleet-memory-sync 盘上 no-op checkout 止血·bm-b 先例同法] '
       '④HQ-MemoryBudgetGate PT4H 在位[Interactive=已裁决默认主体面·任务定义不触碰]·本地闸脚本升级 origin v2 正身 hash MATCH f10cf352） | bm-c loop r1084（CEO 令 2026-10-18 00:2x 机队推广四件套·回执窗 10-25） |')

MSG = 'bm-c memory-gov four-piece receipt row (CEO 令 2026-10-18 00:2x 机队推广四件套: gate v2 首跑 377,015->97,121B + L0 治理终态 87,547B/95 条 + 回灌事故实锚与盘上 no-op 止血 + 闸任务 v2 正身升级) — bm-c loop r1084'


def run(*a, **kw):
    r = subprocess.run(list(a), capture_output=True, cwd=REPO if kw.get('repo', True) else None)
    return r


def attempt():
    run('git', 'fetch', 'origin')
    tip = run('git', 'rev-parse', 'origin/main').stdout.decode().strip()
    blob = run('git', 'show', 'origin/main:' + PATH).stdout
    if not blob:
        print('FATAL: empty origin blob for ' + PATH)
        sys.exit(1)
    row_b = ROW.encode('utf-8')
    if blob.endswith(b'\n'):
        new = blob + row_b + b'\n'
    else:
        new = blob + b'\n' + row_b + b'\n'
    if row_b in blob:
        print('ALREADY-PRESENT: row found on origin, idempotent no-op')
        return tip, None
    import tempfile, os
    tmp = os.path.join(os.environ.get('TEMP', '.'), '_r1084bmc_ledger_row.md')
    with open(tmp, 'wb') as f:
        f.write(new)
    hb = run('git', 'hash-object', '-w', '--no-filters', tmp).stdout.decode().strip()
    os.remove(tmp)
    idx = os.path.join(os.environ.get('TEMP', '.'), '_r1084bmc_ledger_idx')
    env = dict(os.environ)
    import subprocess as sp
    def run_env(*a):
        e = dict(env); e['GIT_INDEX_FILE'] = idx
        return sp.run(list(a), capture_output=True, cwd=REPO, env=e)
    run_env('git', 'read-tree', tip)
    r = run_env('git', 'update-index', '--add', '--cacheinfo', '100644', hb, PATH)
    if r.returncode != 0:
        print('update-index fail: ' + r.stderr.decode('utf-8', 'replace'))
        sys.exit(1)
    tree = run_env('git', 'write-tree').stdout.decode().strip()
    if not tree or len(tree) != 40:
        print('write-tree fail')
        sys.exit(1)
    c = run('git', 'commit-tree', tree, '-p', tip, '-m', MSG)
    sha = c.stdout.decode().strip()
    if len(sha) != 40:
        print('commit-tree fail: ' + c.stderr.decode('utf-8', 'replace'))
        sys.exit(1)
    p = run('git', 'push', 'origin', sha + ':main')
    out = (p.stdout + p.stderr).decode('utf-8', 'replace')
    ok = p.returncode == 0
    print('PUSH rc=%d %s' % (p.returncode, out[-300:]))
    return tip, (sha if ok else None)


tip, sha = None, None
for i in range(3):
    tip, sha = attempt()
    if sha:
        print('LANDED origin/main %s -> %s (parent %s)' % (tip[:12], sha, tip))
        break
    print('retry %d...' % (i + 1))
if not sha:
    print('PUSH-FAILED after retries — report honestly, row NOT on origin')
    sys.exit(1)
