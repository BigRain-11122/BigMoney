# r583 bm-b W100 construct-merge surgical re-parent push #2
# (same-window DIFFERENT-NUMBER double-freeze coexistence per r531 law:
#  bm-a W101 five-face landed on origin mid-flight; merged tree carries
#  BOTH W100 (bm-b) and W101 (bm-a) rows; payload hashed from WORKTREE)
import subprocess, os

def run(*a, **kw):
    return subprocess.run(a, capture_output=True, text=True, **kw)

r = run('git', 'rev-parse', 'HEAD'); assert r.returncode == 0
OLD = r.stdout.strip()
r = run('git', 'rev-parse', 'origin/main'); assert r.returncode == 0
NEW_BASE = r.stdout.strip()
print('old local HEAD =', OLD)
print('origin/main    =', NEW_BASE)

PAYLOAD = [
    'research/PERPETUAL_FACES.md',
    'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py',
    'research/PERPETUAL_N1_W100_PREREG.md',
    'results/_r583bmb_w100_band_gate.py',
    'results/_r583bmb_w100_freeze_edits.py',
    'results/_r583bmb_surgery_push.py',
    'results/_r583bmb_probe_anchors.py',
    'results/_r583bmb_probe_canon.py',
    'results/_r583bmb_probe_close.py',
    'results/_r583bmb_probe_w101_leg.py',
    'results/_r583bmb_probe_w101_leg2.py',
    'results/_r583bmb_probe_w101_priors.py',
    'results/_r583bmb_probe_w100_ref.py',
    'results/_r583bmb_merge_verify.py',
]

tmp_idx = os.path.abspath('results/_r583bmb_tmp_index2')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx): os.remove(tmp_idx)
assert run('git', 'read-tree', NEW_BASE, env=env).returncode == 0

for p in PAYLOAD:
    assert os.path.exists(p), p
    r = run('git', 'hash-object', '-w', p)
    assert r.returncode == 0, (p, r.stderr)
    sha = r.stdout.strip()
    r = run('git', 'update-index', '--add', '--cacheinfo',
            '100644,%s,%s' % (sha, p.replace('/', '/')), env=env)
    assert r.returncode == 0, (p, r.stderr)
print('payload hashed:', len(PAYLOAD), 'worktree files')

r = run('git', 'write-tree', env=env); assert r.returncode == 0, r.stderr
TREE = r.stdout.strip()
r = run('git', 'diff-tree', '--name-only', '-r', '--diff-filter=D', NEW_BASE, TREE)
dels = [l for l in r.stdout.splitlines() if l.strip()]
assert not dels, ('deletion set non-empty', dels)
r = run('git', 'diff-tree', '--name-only', '-r', NEW_BASE, TREE)
delta = set(l.strip() for l in r.stdout.splitlines() if l.strip())
assert delta == set(PAYLOAD), ('delta != payload', sorted(delta ^ set(PAYLOAD)))
print('assertions PASS: deletion-set empty, tree-delta == payload', len(delta))

MSG = """r583 bm-b: W100 FREEZE five-face CONSTRUCT-MERGE with bm-a W101 same-window coexistence (r531 law: different-number double-freeze, band-disjoint by construction; merged tree carries BOTH rows ordered W99<W100<W101 in canon/pf/cfg/leg/frag five faces; bm-a W101 leg is two-state vs W100 (priors ([100] if registered) + dynamic disjoint loop) -> zero amendments needed; merge order+integrity receipt _r583bmb_merge_verify.py ALL PASS + default-wave selftest PASS with both W100+W101 legs); W100 = NINETIETH wave, bm-b 34th owned; A 243_004..245_003 + B 58_751..58_950 both arithmetic continuation CLEAN from W99 tails, zero skips no pin, W92 r370 family; ADMIT receipt _r583bmb_w100_band_gate.py rc0 single state 97-row table; seat MSG-20261002-1615-bmb pre-published r582 r565 law; banned gate 0 matched; prereg anchors rolled to W97 finalize measured keys (head 577,948 K=211,320); push #1 rejected by pre-push claw on diverged base (bm-a W101 files) -> surgical re-parent #2; tick engine self-ignites W100 next tick"""
r = run('git', 'commit-tree', TREE, '-p', NEW_BASE, '-m', MSG)
assert r.returncode == 0, r.stderr
NEWC = r.stdout.strip()
print('new commit =', NEWC)

r = run('git', 'rev-parse', 'main')
assert r.stdout.strip() == OLD, ('main moved', r.stdout)
r = run('git', 'update-ref', 'refs/heads/main', NEWC, OLD)
assert r.returncode == 0, r.stderr
r = run('git', 'push')
print('push rc', r.returncode, (r.stderr or r.stdout).strip()[:300])
assert r.returncode == 0
r = run('git', 'reset', '--mixed', NEWC)
assert r.returncode == 0, r.stderr
run('git', 'fetch', 'origin')
print('unpushed:', run('git', 'rev-list', '--count', 'origin/main..HEAD').stdout.strip())
print('unpulled:', run('git', 'rev-list', '--count', 'HEAD..origin/main').stdout.strip())
st = run('git', 'status', '--porcelain').stdout
print('status:')
print(st)
os.remove(tmp_idx)
