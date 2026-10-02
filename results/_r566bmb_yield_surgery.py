"""r566 bm-b S0 yield surgery: W64 same-band double-freeze yield to bm-a (r511 commit-order law).
Dead r565 session heritage: seat committed+pushed (aeeabf969, B-band amended to W63 published
projection == bm-a's W64 verbatim), freeze uncommitted, 10 shards burned 08:55-09:04 (killed).
Steps: save pool_core_samples rows -> verify+discard products -> remove yielded prereg ->
restore shared faces blocking ff -> pre-check ff blockers.
"""
import subprocess, os, json, sys

os.chdir(r'C:\Fluxgroup\FluxGroup\quant\bigmoney')
repo = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'

def run(*a):
    return subprocess.check_output(list(a), cwd=repo)

# 1. save my appended pool_core_samples rows (worktree beyond HEAD)
head = run('git', 'show', 'HEAD:results/pool_core_samples.jsonl')
cur = open(os.path.join(repo, 'results/pool_core_samples.jsonl'), 'rb').read()
head_lines = head.splitlines(keepends=True)
cur_lines = cur.splitlines(keepends=True)
mine = []
i = 0
for ln in cur_lines:
    if i < len(head_lines) and ln == head_lines[i]:
        i += 1
    else:
        mine.append(ln)
assert len(mine) >= 9, f'unexpected mine row count {len(mine)}'
tmp = os.path.join(os.environ['TEMP'], '_r566bmb_pool_rows.tmp')
open(tmp, 'wb').write(b''.join(mine))
print('saved rows:', len(mine))

# 2. discard local W64 products (verify audit.machine per file, r563 law)
d = os.path.join(repo, 'results/p2cal_ext/n1_w64')
removed = 0
for f in sorted(os.listdir(d)):
    with open(os.path.join(d, f)) as fh:
        j = json.load(fh)
    m = (j.get('audit') or {}).get('machine')
    assert m == 'bm-b', f'{f} owner {m} != bm-b -- ABORT (r525 ownership gate)'
    os.remove(os.path.join(d, f))
    removed += 1
print('removed bm-b-owned W64 products:', removed)

# 3. remove local untracked yielded prereg (origin's bm-a version lands via ff)
os.remove(os.path.join(repo, 'research/PERPETUAL_N1_W64_PREREG.md'))
print('removed local yielded prereg')

# 4. restore shared faces blocking fast-forward (stale-base derived, r296-3/r512)
open(os.path.join(repo, 'results/pool_core_samples.jsonl'), 'wb').write(head)
print('restored pool_core_samples to HEAD (rows saved to temp for post-ff re-append)')

# 5. pre-check ff blockers: dirty files that differ HEAD->origin
dirty = run('git', 'status', '--porcelain').decode().splitlines()
blockers = []
for line in dirty:
    st, path = line[:2], line[3:].strip().strip('"')
    if st.strip() != 'M':
        continue
    r = subprocess.call(['git', 'diff', '--quiet', 'HEAD', 'origin/main', '--', path], cwd=repo)
    if r != 0:
        blockers.append(path)
print('ff blockers (dirty M files differing HEAD->origin):', blockers)
if blockers:
    sys.exit(3)
print('PRE-CHECK OK: ff-only safe with remaining dirty files')
