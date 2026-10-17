# -*- coding: utf-8 -*-
# r989 bm-b: EPBurn handover (3-piece + gen_placeholders dep + RECIPE) CAS direct-push to group repo.
# Method = temp-index surgery on fresh origin tip (zero worktree touch, zero local-copy residue).
# Race-safe: retry loop rebuilds on newest tip if push loses a race.
import subprocess, os, sys, json, datetime

GROUP = r'C:\Fluxgroup\FluxGroup'
DST = 'cph4/fleet/drama-dept-v1/epburn-handover/'
SRC = r'C:\Fluxgroup\MiniGame\Tools\comfy'
BIGM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
RECIPE_LOCAL = os.path.join(BIGM, 'results', '_r989bmb_RECIPE-EPBURN-v1.md')
IDX = os.path.join(BIGM, 'results', '_r989bmb_tmp_index')
MSG = os.path.join(BIGM, 'results', '_r989bmb_delivery_msg.txt')
RECEIPT = os.path.join(BIGM, 'results', '_r989bmb_epburn_delivery_receipt.json')

FILES = [
    (os.path.join(SRC, 'drama_ep_runner.ps1'), DST + 'drama_ep_runner.ps1'),
    (os.path.join(SRC, 'drama_ep_burn.py'), DST + 'drama_ep_burn.py'),
    (os.path.join(SRC, 'drama_ep_assemble.py'), DST + 'drama_ep_assemble.py'),
    (os.path.join(SRC, 'gen_placeholders.py'), DST + 'gen_placeholders.py'),
    (RECIPE_LOCAL, DST + 'RECIPE-EPBURN-v1.md'),
]

def git(args, env=None, timeout=180):
    e = dict(os.environ)
    if env:
        e.update(env)
    p = subprocess.run(['git', '-C', GROUP] + args, capture_output=True, timeout=timeout, env=e)
    return p.returncode, p.stdout.decode('utf-8', 'replace').strip(), p.stderr.decode('utf-8', 'replace').strip()

def build_and_push(attempt):
    rc, _, err = git(['fetch', 'origin'], timeout=300)
    print('FETCH rc=%d %s' % (rc, err[:120]))
    if rc != 0:
        return None, 'fetch fail: ' + err[:200]
    rc, tip, _ = git(['rev-parse', 'origin/main'])
    if rc != 0 or len(tip) != 40:
        return None, 'rev-parse fail'
    print('TIP ' + tip[:12])
    rc, out, _ = git(['ls-tree', '--name-only', tip, 'cph4/fleet/drama-dept-v1/'])
    if 'epburn-handover' in out:
        return None, 'target dir already exists on tip - abort (re-delivery decision needed)'
    env_idx = {'GIT_INDEX_FILE': IDX}
    rc, _, err = git(['read-tree', tip], env=env_idx)
    if rc != 0:
        return None, 'read-tree fail: ' + err[:200]
    for local, repo_path in FILES:
        if not os.path.exists(local):
            return None, 'missing local ' + local
        rc, blob, err = git(['hash-object', '-w', local])
        if rc != 0 or len(blob) != 40:
            return None, 'hash-object fail %s %s' % (local, err[:120])
        rc2, _, err2 = git(['update-index', '--add', '--cacheinfo', '100644,%s,%s' % (blob, repo_path)], env=env_idx)
        if rc2 != 0:
            return None, 'update-index fail ' + err2[:120]
        print('ADD %s %s' % (repo_path, blob[:12]))
    rc, tree, err = git(['write-tree'], env=env_idx)
    if rc != 0 or len(tree) != 40:
        return None, 'write-tree fail ' + err[:120]
    with open(MSG, 'w', encoding='utf-8') as f:
        f.write('drama-dept EPBurn toolchain handover (bm-b r989): runner v2.3 + burn + assemble + gen_placeholders dep + RECIPE\n\n'
                'E1 five-receipts item delivery leg (O-20261015-1741 CEO card dispatch, POOL-0015 production line).\n'
                'Source of truth: MiniGame/Tools/comfy/ (bm-b local). Consumers: bm-a/bm-c EP line (drama-001-stockera 60 eps).\n'
                'Porting note: scripts embed bm-b absolute paths - see RECIPE sec.3 port table.')
    rc, commit, err = git(['commit-tree', tree, '-p', tip, '-F', MSG])
    if rc != 0 or len(commit) != 40:
        return None, 'commit-tree fail ' + err[:120]
    print('COMMIT ' + commit[:12])
    rc, out, err = git(['push', 'origin', commit + ':refs/heads/main'], timeout=300)
    if rc != 0:
        return None, 'push rejected: ' + err[:200]
    return {'attempt': attempt, 'base_tip': tip, 'tree': tree, 'commit': commit}, 'ok'

result, note = None, 'not run'
for attempt in (1, 2, 3):
    result, note = build_and_push(attempt)
    if result:
        break
    print('RETRY_SCHEDULED: %s' % note)
if result:
    git(['fetch', 'origin'], timeout=300)
    rc, newtip, _ = git(['rev-parse', 'origin/main'])
    verified = (rc == 0 and newtip == result['commit'])
    files_ok = {}
    for _, rp in FILES:
        rc2, _, _ = git(['cat-file', '-e', 'origin/main:' + rp])
        files_ok[rp] = (rc2 == 0)
    result['verified'] = verified
    result['files_on_origin'] = files_ok
    result['ts'] = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    result['note'] = note
    with open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print('DELIVERY_VERIFIED=%s NEWTIP=%s' % (verified, newtip[:12]))
    print('RECEIPT_WRITTEN ' + RECEIPT)
else:
    print('DELIVERY_FAILED: ' + note)
    with open(RECEIPT, 'w', encoding='utf-8') as f:
        json.dump({'ts': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00'), 'failed': True, 'note': note}, f, ensure_ascii=False, indent=1)
    sys.exit(2)
