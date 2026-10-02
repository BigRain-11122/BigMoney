# -*- coding: utf-8 -*-
# r375 bm-c wrap surgical re-parent push #2 v2 (bytes-mode git; GBK crash fix).
# Origin advanced with peer wraps: 30 same-day idempotent derive faces collide
# -> r505 bm-b precedent: take the fresher wall-clock side ONCE = drop them
# from my payload (origin side stands; worktree syncs at checkout).
# Append-only shared faces carry via union: CODELY.md (pit line),
# results/pool_core_samples.jsonl, results/x2_watch_log.jsonl (dict-gate r570).
# My-machine-exclusive faces carry from my wrap commit blobs. CAS + assertions.
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREAT = 0x08000000
UNION_FACES = ['CODELY.md', 'results/pool_core_samples.jsonl', 'results/x2_watch_log.jsonl']
MY_EXCLUSIVE = [
    'state-bm-c.json', 'fleet/machines/bm-c.json', 'round_reports-bm-c.md',
    'research/HANDOVER.md',
    'results/_r375bmc_w102_surgery_push.py', 'results/_r375bmc_close.py',
    'results/_r375bmc_surgery2.py',
    'results/p1d_gates.json', 'results/autofill_state.bm-c.json',
    'results/dispatcher_state.bm-c.json', 'results/saturation_engine_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json', 'results/regime_state.bm-c.json',
    'results/update_status.bm-c.json', 'results/futures_update_status.bm-c.json',
    'results/lhb_update_status.bm-c.json', 'results/compute_audit.bm-c.json',
    'results/token_usage.bm-c.json', 'results/pool_dualrun.bm-c.jsonl',
    'results/fund_premium_status.json',
    'fleet/inbox/processed/MSG-20261002-1642-bmc-w102-seat.md',
]


def run(*a, **kw):
    return subprocess.run(a, capture_output=True, cwd=REPO, creationflags=CREAT, **kw)


def out(r):
    return r.stdout.decode('utf-8', 'replace')


r = run('git', 'rev-parse', 'HEAD'); assert r.returncode == 0, out(r)
OLD = out(r).strip()
r = run('git', 'rev-parse', 'origin/main'); assert r.returncode == 0, out(r)
NEW_BASE = out(r).strip()
print('local HEAD =', OLD[:12], ' origin/main =', NEW_BASE[:12])

r = run('git', 'merge-base', OLD, NEW_BASE)
BASE = out(r).strip()
r = run('git', 'diff', '--name-only', BASE, NEW_BASE)
their = set(l.strip() for l in out(r).splitlines() if l.strip())

# ---- union faces re-derived vs NEW base ----------------------------------------
# CODELY: my r375 pit line inserted before ### Reference of the NEW base blob
src = os.path.join(REPO, 'CODELY.md')
mine_lf = open(src, 'rb').read().replace(b'\r\n', b'\n').decode('utf-8')
my_pit = [ln for ln in mine_lf.split('\n') if 'r375 bm-c] PS 超长命令串' in ln]
assert len(my_pit) == 1, my_pit
r = run('git', 'show', NEW_BASE + ':CODELY.md')
assert r.returncode == 0, out(r)
o_text = r.stdout.decode('utf-8')
assert '\r' not in o_text
o_lines = o_text.split('\n')
assert o_lines.count('### Reference') == 1
if my_pit[0] in o_lines:
    print('CODELY: pit line already on new base')
else:
    ref_i = o_lines.index('### Reference')
    union = o_lines[:ref_i] + [my_pit[0]] + o_lines[ref_i:]
    open(src, 'wb').write('\n'.join(union).encode('utf-8').replace(b'\n', b'\r\n'))
    print('CODELY re-union vs new base: pit line carried')

# pool_core_samples + x2_watch_log: union origin lines + local extras (dict gate)
import json as _j
for face in ('results/pool_core_samples.jsonl', 'results/x2_watch_log.jsonl'):
    fp = os.path.join(REPO, face)
    r = run('git', 'show', NEW_BASE + ':' + face)
    assert r.returncode == 0, (face, out(r))
    base_text = r.stdout.decode('utf-8')
    base_lines = base_text.rstrip('\n').split('\n') if base_text.strip() else []
    base_set = set(base_lines)
    local_lines = [ln for ln in open(fp, 'rb').read().decode('utf-8').splitlines() if ln.strip()]
    extras = []
    for ln in local_lines:
        if ln not in base_set:
            try:
                if isinstance(_j.loads(ln), dict):
                    extras.append(ln)
            except Exception:
                pass
    merged = base_lines + extras
    open(fp, 'wb').write(('\n'.join(merged) + '\n').encode('utf-8').replace(b'\n', b'\r\n'))
    print('%s union: base %d + local extras %d' % (face, len(base_lines), len(extras)))

# ---- build tree: NEW_BASE + union faces (worktree, clean filter) + my blobs ----
tmp_idx = os.path.abspath(os.path.join(REPO, 'results', '_r375bmc_tmp_index2'))
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)
assert run('git', 'read-tree', NEW_BASE, env=env).returncode == 0
assert run('git', 'add', '--', *UNION_FACES, env=env).returncode == 0

carried = []
for p in MY_EXCLUSIVE:
    fp = os.path.join(REPO, p)
    if not os.path.exists(fp):
        continue
    r = run('git', 'ls-tree', OLD, '--', p)
    line = out(r).strip()
    if not line:
        # untracked new file (e.g. this surgery tool) -> stage from worktree
        assert run('git', 'add', '--', p, env=env).returncode == 0
        carried.append(p)
        continue
    left, _sep, _path = line.splitlines()[0].partition('\t')
    mode, typ, sha = left.split()
    assert typ == 'blob' and len(sha) == 40, (p, left)
    r2 = run('git', 'update-index', '--add', '--cacheinfo',
             '%s,%s,%s' % (mode, sha, p), env=env)
    assert r2.returncode == 0, (p, out(r2))
    carried.append(p)

r = run('git', 'write-tree', env=env); assert r.returncode == 0, out(r)
TREE = out(r).strip()

r = run('git', 'diff-tree', '--name-only', '-r', '--diff-filter=D', NEW_BASE, TREE)
dels = [l for l in out(r).splitlines() if l.strip()]
assert not dels, ('deletion set non-empty', dels)
r = run('git', 'diff-tree', '--name-only', '-r', NEW_BASE, TREE)
delta = set(l.strip() for l in out(r).splitlines() if l.strip())
assert delta <= set(carried) | set(UNION_FACES), \
    ('delta beyond payload', sorted(delta - set(carried) - set(UNION_FACES)))
print('assertions PASS: deletion-set empty, delta(%d) = %d carried + %d union'
      % (len(delta), len(carried), len(UNION_FACES)))

msg_file = os.path.abspath(os.path.join(REPO, '..', '.codely-cli', 'scratch',
                                        '_r375bmc_wrap_msg.txt'))
MSG = open(msg_file, encoding='utf-8').read().strip()
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', MSG)
assert r.returncode == 0, out(r)
NEWC = out(r).strip()
print('new commit =', NEWC)

r = run('git', 'rev-parse', 'main')
assert out(r).strip() == OLD, ('main moved mid-surgery (CAS abort, re-run)', out(r))
r = run('git', 'update-ref', 'refs/heads/main', NEWC, OLD)
assert r.returncode == 0, out(r)
r = run('git', 'push', 'origin', 'main')
print('push rc =', r.returncode)
if r.returncode != 0:
    print(out(r)); print(r.stderr.decode('utf-8', 'replace'))
    sys.exit(1)

assert run('git', 'reset', '--mixed', NEWC).returncode == 0
r = run('git', 'status', '--porcelain')
missing = [l[3:].strip() for l in out(r).splitlines()
           if l.startswith(' D') or l.startswith('D ')]
if missing:
    r2 = run('git', 'checkout', 'HEAD', '--', *missing)
    assert r2.returncode == 0, (missing[:4], out(r2))
print('worktree synced: %d missing faces checked out' % len(missing))
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)

run('git', 'fetch', 'origin')
r = run('git', 'rev-list', '--left-right', '--count', 'main...origin/main')
print('delivery proof (ahead/behind):', out(r).strip())
r = run('git', 'ls-tree', '--name-only', 'origin/main', '--', 'results/p2cal_ext/n1_w102/')
print('W102 shards on origin:', len([l for l in out(r).splitlines() if l.strip()]))
print('SURGERY2_OK')
