# -*- coding: utf-8 -*-
# r336 bm-c: working-tree heal after re-anchor -- restore origin-owned faces,
# verify paper ledgers are local-subset-of-origin before restore (r294 law).
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
]
D_RESTORE = [
    'fleet/inbox/processed/MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md',
    'research/PERPETUAL_N1_W28_PREREG.md', 'results/_r523bmb_w28_band_gate.py',
    'results/_r539bma_bookkeeping.py',
] + ['results/p2cal_ext/n1_w27/shard-%d-of-12.json' % i for i in range(12)] + [
    'results/p2cal_ext/n1_w28/shard-0-of-12.json',
]
PAPER = ['results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
         'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
         'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json']

# 1. paper ledgers: local must be subset (prefix) of origin before restore
def deep_prefix(local, origin):
    if isinstance(local, list) and isinstance(origin, list):
        if len(local) > len(origin):
            return False
        return all(deep_prefix(a, b) for a, b in zip(local, origin))
    if isinstance(local, dict) and isinstance(origin, dict):
        for k, v in local.items():
            if k not in origin:
                return False
            if not deep_prefix(v, origin[k]):
                return False
        return True
    if isinstance(local, (int, float)) and isinstance(origin, (int, float)):
        return abs(local - origin) < 1e-9 or local == origin
    return local == origin

paper_ok = True
for f in PAPER:
    o = json.loads(git('show', 'HEAD:' + f).stdout.decode('utf-8'))
    l = json.load(open(os.path.join(R, f.replace('/', os.sep)), encoding='utf-8'))
    ok = deep_prefix(l, o)
    print('PAPER-SUBSET', f, 'local-subset-of-origin' if ok else 'DIVERGENT')
    if not ok:
        paper_ok = False
x2_local_path = os.path.join(R, 'results', 'x2_watch_log.jsonl')
x2_local = [ln for ln in open(x2_local_path, encoding='utf-8').read().splitlines() if ln.strip()]
x2_origin = [ln for ln in git('show', 'HEAD:results/x2_watch_log.jsonl').stdout.decode('utf-8').splitlines() if ln.strip()]
x2_subset = x2_local == x2_origin[:len(x2_local)] and len(x2_local) <= len(x2_origin)
print('X2-SUBSET local=%d origin=%d ->' % (len(x2_local), len(x2_origin)), 'subset' if x2_subset else 'DIVERGENT')

# 2. bulk checkout
if paper_ok and x2_subset:
    targets = CHECKOUT_M + D_RESTORE + PAPER + ['results/x2_watch_log.jsonl']
    # multi-pathspec checkout: pre-validate every path exists in HEAD (r326 lesson:
    # one invalid path silently aborts the whole batch)
    invalid = []
    for f in targets:
        rc = subprocess.run(['git', '-C', R, 'cat-file', '-e', 'HEAD:' + f], capture_output=True).returncode
        if rc != 0:
            invalid.append(f)
    if invalid:
        print('INVALID PATHS (skipped):', invalid)
    valid = [f for f in targets if f not in invalid]
    git('checkout', '--', *valid)
    print('CHECKED-OUT', len(valid), 'files')
else:
    print('ABORT checkout of paper/x2 faces -- manual union required')

# 3. stale local inbox copy of already-processed MSG (origin moved it to processed/)
inbox_local = os.path.join(R, 'fleet', 'inbox', 'MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md')
proc_git = git('show', 'HEAD:fleet/inbox/processed/MSG-20261001-213x-bmb-bmc-bma-ALL-w25-finalize-ledger-419548.md').stdout
if os.path.exists(inbox_local):
    same = open(inbox_local, 'rb').read() == proc_git
    print('INBOX-MSG same-as-processed:', same)
    if same:
        os.remove(inbox_local)
        print('removed stale local inbox copy (already processed by bm-a r539, r516 move-verify law)')
else:
    print('INBOX-MSG absent locally')

st = git('status', '--porcelain').stdout.decode().strip().splitlines()
print('REMAINING_DIRTY count=%d' % len(st))
for ln in st:
    print('  D|', ln)
