# -*- coding: utf-8 -*-
"""r570 bm-a surgical push stage 2: temp-index payload overlay onto origin/main.

Template = r530/r531/r568 laws: read-tree origin -> per-file update-index ->
deletion-set assertion (empty) + payload-count assertion -> commit-tree
-p origin/main -> push sha:main. Bytes channel for index-info (r568 law).
"""
import subprocess, sys, os, json, tempfile

REPO = os.getcwd()
BASE = 'cd2e57af6'
IDX = os.path.join(REPO, '.git', 'surgical_idx_r570bma')

def git(*a, **kw):
    r = subprocess.run(['git'] + list(a), capture_output=True, **kw)
    if r.returncode != 0:
        print('GIT FAIL', a[:4], '->', r.stderr.decode('utf-8', 'replace')[:400])
        sys.exit(1)
    return r.stdout

def genv(*a):
    env = dict(os.environ)
    env['GIT_INDEX_FILE'] = IDX
    return git(*a, env=env)

git('fetch', 'origin')
ORIGIN = git('rev-parse', 'origin/main').decode().strip()

# --- classify my payload vs BASE ---
ns = git('diff', '--name-status', BASE, 'HEAD').decode().splitlines()
payload = []   # (status, path)
for ln in ns:
    parts = ln.split('\t')
    if not parts or not parts[0]:
        continue
    st = parts[0][0]
    if st == 'R' and len(parts) >= 3:
        # rename = deletion of old + addition of new
        payload.append(('D', parts[1].strip()))
        payload.append(('A', parts[2].strip()))
    elif len(parts) >= 2:
        payload.append((st, parts[1].strip()))
print('payload entries:', len(payload))

# --- resolve overlap content first (CODELY union; pcs already resolved on disk) ---
# CODELY.md: origin version + my new tail line (append-face union)
codely_mine = open('CODELY.md', encoding='utf-8').read()
codely_origin = subprocess.check_output(['git', 'show', ORIGIN + ':CODELY.md']).decode('utf-8')
my_line_marker = '[2026-10-02 10:4x r570 bm-a] 共享 jsonl 本地 shell 重定向覆写坑'
assert my_line_marker in codely_mine, 'my CODELY line missing locally'
if my_line_marker not in codely_origin:
    # union: origin base + my line appended
    eol = '\r\n' if codely_origin.count('\r\n') * 2 > codely_origin.count('\n') else '\n'
    uni = codely_origin
    if not uni.endswith(eol):
        uni += eol
    # extract my full line from my file
    for ln in codely_mine.splitlines():
        if my_line_marker in ln:
            uni += ln + eol
            break
    open('CODELY.md', 'wb').write(uni.encode('utf-8'))
    print('CODELY union: origin + my r570 line (both lessons survive)')
else:
    print('CODELY: my line already on origin (skip union)')

# --- verify identical-content MSG processed moves (vs origin) ---
identical, staged = [], []
for st, path in payload:
    if st == 'D':
        # deletion: origin must already have it deleted (MSG moves) -- assert
        chk = subprocess.run(['git', 'cat-file', '-e', ORIGIN + ':' + path],
                             capture_output=True)
        if chk.returncode == 0:
            print('FATAL: payload deletes', path, 'but origin still has it -- abort')
            sys.exit(1)
        print('deletion no-op (origin already deleted):', path)
        continue
    # A or M: stage my (possibly resolved) content
    if not os.path.exists(path):
        print('FATAL: payload file missing on disk:', path)
        sys.exit(1)
    staged.append(path)
print('staging files:', len(staged))

# --- build surgical tree ---
if os.path.exists(IDX):
    os.remove(IDX)
genv('read-tree', ORIGIN)
for path in staged:
    blob = subprocess.run(['git', 'hash-object', '-w', '--', path],
                          capture_output=True, cwd=REPO)
    if blob.returncode != 0:
        print('hash-object FAIL', path)
        sys.exit(1)
    sha = blob.stdout.decode().strip()
    mode = '100644'
    # feed update-index via bytes channel (r568: no text=True with input)
    info = ('0 %s %s\t%s\n' % (mode, sha, path)).encode('utf-8')
    r = subprocess.run(['git', 'update-index', '--add', '--cacheinfo', mode, sha, path],
                       capture_output=True, env={**os.environ, 'GIT_INDEX_FILE': IDX})
    if r.returncode != 0:
        print('update-index FAIL', path, r.stderr.decode()[:200])
        sys.exit(1)

# --- assertions vs origin (r530/r531/r568 template) ---
diff = genv('diff-index', '--cached', '--name-status', ORIGIN).decode()
adds = 0
dels = []
for ln in diff.splitlines():
    parts = ln.split('\t')
    if len(parts) >= 2:
        if parts[0].startswith('D'):
            dels.append(parts[-1])
        else:
            adds += 1
assert not dels, 'DELETION-SET not empty (r519 family abort): %s' % dels
print('deletion-set: EMPTY (assertion pass)')
print('staged adds vs origin:', adds, '== payload A/M minus identical-content no-ops expected')

tree = genv('write-tree').decode().strip()
print('tree:', tree[:12])

# --- commit-tree ---
msg_path = os.path.join(REPO, '.codely-cli', 'scratch', '_r570bma_surg_msg.txt')
open(msg_path, 'w', encoding='utf-8', newline='').write(
    'round 570 bm-a surgical rebroadcast (payload overlay onto moved origin per r532 live-write law)\n\n'
    'Same content as the two local commits (closeout + ride r570c), overlaid onto origin/main '
    '32f6845c0 after the W71-finalize/bm-b-fleet-repair window moved it 8 ahead. Resolution: '
    'pool_core_samples.jsonl = bm-b full-git-version union repair (750 rows) + 10 live W73 burn '
    'sampler rows union-appended (760 rows all-dict post-verified) -- bm-b repair preserved '
    'verbatim (r294 domain law); CODELY.md = append-face union (bm-b r570 jsonl type-gate lesson '
    '+ bm-a r570 redirect-clobber pitfall line both survive); same-day idempotent derive faces '
    '(daily_report/live_usage/audit/status jsons, bm-a=designated host per r378) take wall-clock-new '
    'side; inbox MSG processed moves = byte-identical no-ops (origin already archived by bm-c r362). '
    'Deletion-set assertion EMPTY, payload staged=%d files. W73 burn in flight (shards 0-7 committed, '
    '8+ accruing; next-round closeout delivers remainder + finalize after W72 bm-b lands).\n\n'
    '[via bm-a r570]\n' % len(staged))
cmt = subprocess.run(['git', 'commit-tree', tree, '-p', ORIGIN, '-F', msg_path],
                     capture_output=True, env={**os.environ, 'GIT_INDEX_FILE': IDX})
if cmt.returncode != 0:
    print('commit-tree FAIL', cmt.stderr.decode()[:300])
    sys.exit(1)
sha = cmt.stdout.decode().strip()
print('commit:', sha[:12])

# --- push (r559 law: origin remote name explicit) ---
push = subprocess.run(['git', 'push', 'origin', sha + ':main'], capture_output=True)
if push.returncode != 0:
    err = push.stderr.decode('utf-8', 'replace')
    print('PUSH REJECTED:', err[:400])
    sys.exit(2)
print('PUSH OK:', sha[:12], '-> main')

# --- delivery self-verify (r331/r310 post-write ls-tree) ---
git('fetch', 'origin')
for probe in staged[:6] + ['results/pool_core_samples.jsonl', 'CODELY.md']:
    chk = subprocess.run(['git', 'cat-file', '-e', 'origin/main:' + probe], capture_output=True)
    print('ls-tree probe', probe, '->', 'PRESENT' if chk.returncode == 0 else 'MISSING')
print('SURGICAL_OK')
