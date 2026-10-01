# -*- coding: utf-8 -*-
# r336 bm-c: surgical push #2 -- W29 freeze set + S6 fresh outputs + bm-c lane
# files + round tool scripts. r523-3 pattern (fresh parent, retry loop).
import io, sys, os, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

FILES = [
    # W29 freeze set
    'research/PERPETUAL_FACES.md', 'research/PERPETUAL_N1_W29_PREREG.md',
    'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
    'results/_r336bmc_w29_band_gate.py',
    # round tool scripts (provenance)
    'results/_r336bmc_surgical_push1.py', 'results/_r336bmc_integrate.py',
    'results/_r336bmc_heal.py', 'results/_r336bmc_restore2.py',
    'results/_r336bmc_paper_dissect.py',
    # S6 fresh outputs (same-day idempotent regen, wall-clock newer side r505)
    'docs/daily_report/REPORT-2026-10-01.json', 'docs/daily_report/REPORT-2026-10-01.md',
    'docs/live_usage/LIVE-2026-10-01.json', 'docs/live_usage/LIVE-2026-10-01.md',
    'docs/live_usage/LIVE-latest.json', 'docs/live_usage/LIVE-latest.md',
    'results/_attrition_guard_scan.json', 'results/compute_audit.json',
    'results/dashboard_status.json', 'results/dashboard_status.js',
    'results/fundamental_b_layer_filter.json',
    'results/paper_export/export-2026-09-30.json', 'results/paper_export/latest.json',
    'results/regime_state.json', 'results/token_usage.json', 'results/update_status.json',
    'results/futures_update_status.json', 'results/lhb_update_status.json',
    # bm-c lane files (single-writer local)
    'results/autofill_state.bm-c.json', 'results/compute_audit.bm-c.json',
    'results/dispatcher_state.bm-c.json', 'results/fund_premium_status.json',
    'results/futures_update_status.bm-c.json', 'results/lhb_update_status.bm-c.json',
    'results/pool_dualrun.bm-c.jsonl', 'results/regime_state.bm-c.json',
    'results/saturation_engine/face_bm-c.json', 'results/saturation_engine_state.bm-c.json',
    'results/token_usage.bm-c.json', 'results/update_status.bm-c.json',
]

def git(*a, env=None, check=True):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True, env=env)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.returncode, r.stderr.decode('utf-8', 'replace')[:300])
        sys.exit(1)
    return r

# stale local inbox duplicate of an already-processed MSG (byte-content identical
# to the processed/ copy on origin; bm-a r539 processed it; the W25 chain claim
# is verified in this round's W26 finalize work) -- remove before commit
inbox = os.path.join(R, 'fleet', 'inbox',
                     'MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md')
if os.path.exists(inbox):
    os.remove(inbox)
    print('removed stale local inbox duplicate (content preserved in processed/ on origin)')

git('fetch', 'origin')
parent = git('rev-parse', 'origin/main').stdout.decode().strip()
print('PARENT', parent[:12])

tmp_idx = os.path.join(os.environ.get('TEMP', r'C:\Windows\Temp'), 'r336bmc_idx2')
env = dict(os.environ, GIT_INDEX_FILE=tmp_idx)
if os.path.exists(tmp_idx):
    os.remove(tmp_idx)
git('read-tree', parent, env=env)
for f in FILES:
    git('add', '--', f, env=env)
staged = git('diff', '--cached', '--name-only', parent, env=env).stdout.decode().strip().splitlines()
assert sorted(staged) == sorted(FILES), 'staged set mismatch: %s' % staged
tree = git('write-tree', env=env).stdout.decode().strip()
print('TREE', tree[:12], 'staged', len(staged), 'files')

MSG = ('r336 W29 freeze: EIGHTEENTH engine wave bm-c sixth-owned (rotation slot W29=bm-c per '
       'W28 row verbatim, 26+3 rotation law), BOTH tails arithmetic-clean A 101_004..103_003 / '
       'B 40_651..40_850 no-skip -- W28 row W29+ WARNING projection verified machine-side by '
       'ADMIT receipt _r336bmc_w29_band_gate.py (27-row pre-W29 scan + N3-R1 leg 70_000..70_005 '
       '+ probe-seed cluster 95_000..95_003 r335 leg + SEED_REGISTRY 158 values + lfc/options '
       'actuals, no skip R250), prereg PERPETUAL_N1_W29_PREREG.md (anchor W26 finalize r336 bm-c '
       'ledger 421,748, cumulative K=57,320 expected, S5 anchors=W26 measured mu -0.09192 sigma '
       '0.24472 p95 0.3273 k-lift +0.0011; bm-c resident-instance restart law r330 carried in '
       'sec.6) + law sec.4 W29 row + WAVE_CONFIGS/N1_BANDS[29] + selftest W29 materializer leg '
       '(deps W17..W26 present, W27/W28 FAIL-CLOSED runtime per r307) + banned gate ADMIT + '
       'n1 selftest green (W29 leg) + pf selftest 8/8; W30+ projection machine-fact: A '
       '103_004..105_003 CLEAN, B 40_851..41_050 REFUSED [41000 registry point] = first '
       'B-side forced-skip candidate since W26, law row warning text matches gate receipt; '
       '+ S6 34 legs rc0 holiday window (dualrun streak 23/3 ZERO-DRIFT, attrition CLEAN, '
       'lane guards honest no-ops, REPORT/LIVE/dscore-class faces regenerated fresher r505 '
       'law) + bm-c lane files + integration heal provenance (adopted crashed r336 attempt '
       'W26 finalize already pushed 96d1b5544; reset+checkout alignment restored 58 '
       'origin-owned faces incl. W27/W28 products, scripts/law rows; paper ledgers '
       'adjudicated identical-science stale-guard-face -> origin side)')
sha = None
for attempt in range(4):
    if attempt > 0:
        git('fetch', 'origin')
        parent = git('rev-parse', 'origin/main').stdout.decode().strip()
        print('RETRY with new parent', parent[:12])
    sha = git('commit-tree', tree, '-p', parent, '-m', MSG).stdout.decode().strip()
    pr = subprocess.run(['git', '-C', R, 'push', 'origin', sha + ':refs/heads/main'], capture_output=True)
    if pr.returncode == 0:
        print('PUSHED', sha)
        break
    print('push rejected:', pr.stderr.decode('utf-8', 'replace')[:200])
else:
    print('PUSH FAILED after retries')
    sys.exit(1)

git('fetch', 'origin')
for f in FILES[:5]:
    rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'origin/main:' + f], capture_output=True).returncode
    print('DELIVERED' if rc == 0 else 'MISSING', f)
nxt = git('rev-list', '--count', sha + '..origin/main').stdout.decode().strip()
print('ORIGIN_MOVED_AFTER_ME', nxt)
print('SURGICAL_PUSH2_OK', sha)
