# -*- coding: utf-8 -*-
# r336 bm-c: bulk origin-side restore (paper divergence adjudicated: identical science,
# stale local guard-face -> origin newer side per r505) + inbox MSG two-version diff.
import io, sys, os, json, subprocess
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
R = r'K:\Fluxgroup\FluxGroup\quant\bigmoney'

def git(*a, check=True):
    r = subprocess.run(['git', '-C', R] + list(a), capture_output=True)
    if check and r.returncode != 0:
        print('GIT FAIL', a, r.returncode, r.stderr.decode('utf-8', 'replace')[:300])
        sys.exit(1)
    return r

CHECKOUT_M = [
    'fleet/machines/bm-a.json', 'state-bm-a.json', 'round_reports-bm-a.md',
    'research/PERPETUAL_FACES.md', 'scripts/perpetual_faces.py', 'scripts/perpetual_faces_n1.py',
    'results/ah_panel_status.json', 'results/autofill_state.bm-a.json', 'results/autofill_state.bm-b.json',
    'results/compute_audit.bm-a.json', 'results/futures_update_status.bm-a.json',
    'results/heat_update_status.bm-a.json', 'results/heat_update_status.json',
    'results/lhb_update_status.bm-a.json', 'results/moneyflow_update_status.json',
    'results/options_update_status.json', 'results/p1d_gates.json', 'results/pool_dualrun.bm-a.jsonl',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/regime_state.bm-a.json', 'results/repo_update_status.json',
    'results/saturation_engine/face_bm-a.json', 'results/saturation_engine/face_bm-b.json',
    'results/saturation_engine/history_bm-a.jsonl', 'results/saturation_engine/history_bm-b.jsonl',
    'results/saturation_engine/ledger_bm-a.jsonl', 'results/saturation_engine/ledger_bm-b.jsonl',
    'results/saturation_engine/state_bm-a.json', 'results/saturation_engine/state_bm-b.json',
    'results/sina_mf_update_status.json', 'results/t35_open_fill_verify.json',
    'results/token_usage.bm-a.json', 'results/update_status.bm-a.json',
    'results/x2_watch_log.jsonl',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
]
D_RESTORE = [
    'fleet/inbox/processed/MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md',
    'research/PERPETUAL_N1_W28_PREREG.md', 'results/_r523bmb_w28_band_gate.py',
    'results/_r539bma_bookkeeping.py',
] + ['results/p2cal_ext/n1_w27/shard-%d-of-12.json' % i for i in range(12)] + [
    'results/p2cal_ext/n1_w28/shard-0-of-12.json',
]
targets = CHECKOUT_M + D_RESTORE
invalid = [f for f in targets
           if subprocess.run(['git', '-C', R, 'cat-file', '-e', 'HEAD:' + f], capture_output=True).returncode != 0]
if invalid:
    print('INVALID (skip):', invalid)
valid = [f for f in targets if f not in invalid]
git('checkout', '--', *valid)
print('CHECKED-OUT', len(valid), 'files')

# inbox MSG: diff local unread copy vs origin processed copy
inbox_local = os.path.join(R, 'fleet', 'inbox', 'MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md')
proc = git('show', 'HEAD:fleet/inbox/processed/MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md').stdout.decode('utf-8', 'replace')
loc = open(inbox_local, encoding='utf-8', errors='replace').read()
pl, ll = proc.splitlines(), loc.splitlines()
print('processed lines=%d local lines=%d' % (len(pl), len(ll)))
extra_proc = [ln for ln in pl if ln not in ll]
extra_loc = [ln for ln in ll if ln not in pl]
print('lines only in processed:', len(extra_proc))
for ln in extra_proc[:8]:
    print('  P|', ln[:150])
print('lines only in local:', len(extra_loc))
for ln in extra_loc[:8]:
    print('  L|', ln[:150])

st = git('status', '--porcelain').stdout.decode().strip().splitlines()
print('REMAINING_DIRTY count=%d' % len(st))
for ln in st:
    print('  D|', ln)
