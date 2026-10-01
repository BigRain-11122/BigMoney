# r509 continuation: finish integration commit + CAS (steps 7b-9)
import subprocess, json, sys, os
sys.path.insert(0, os.getcwd())
sys.path.insert(0, 'scripts')

def run(cmd, check=True):
    r = subprocess.run(cmd, capture_output=True)
    if check and r.returncode != 0:
        print("FAIL CMD:", cmd, "\nOUT:", r.stdout.decode('utf-8', 'replace')[-1500:],
              "\nERR:", r.stderr.decode('utf-8', 'replace')[-1500:])
        sys.exit(1)
    return r

BASE = 'origin/main'
RESTORE = [
    'scripts/saturation_engine.py', 'scripts/perpetual_faces.py',
    'scripts/perpetual_faces_n1.py', 'monitor/build_status.py',
    'research/PERPETUAL_FACES.md', 'research/PERPETUAL_N1_W10_PREREG.md',
    'Tools/register_satengine_task.ps1', 'Tools/iteration_prompt.txt',
    'dashboard.html', 'results/p2cal_ext/n1_w10', 'results/pool_claims',
    'results/saturation_engine', 'results/_r508bmb_s6_log.txt',
    'results/_r508bmb_s6_runner.ps1', 'results/_r508bmb_s6_runner2.ps1',
    'results/_r508bmb_w10_band_gate.py', 'state.json', 'fleet/machines/bm-b.json',
    'logs/iteration-loop/round_reports.md', 'results/autofill_state.bm-b.json',
    'results/crash_fuse.bm-b.json', 'results/compute_audit.bm-b.json',
    'results/token_usage.bm-b.json', 'results/futures_update_status.bm-b.json',
    'results/lhb_update_status.bm-b.json', 'results/minute_feed_status.bm-b.json',
    'results/minute_feed_status.json', 'results/regime_state.bm-b.json',
    'results/update_status.bm-b.json', 'results/etf_daily_pull_status.json',
    'results/astock_daily_update_status.json', 'results/pool_dualrun.bm-b.jsonl',
    'results/runnable_pool.bm-b.json', 'results/t35_open_fill_verify.json',
    'results/prospect_paper/_summary.json', 'results/prospect_promotion/_summary.json',
    'results/daily_scorecard.json', 'results/p1d_gates.json', 'results/x2_watch_log.jsonl',
    'results/paper/COMPOSITE-CE-01_paper.json', 'results/paper/COMPOSITE-CE-02_paper.json',
    'results/paper/DROUGHT-CE-01_paper.json', 'results/paper/ENGULF-CE-01_paper.json',
    'results/paper/NEEDLE-DE-01_paper.json', 'results/paper/VOLATILITY-CE-01_paper.json',
    'results/paper_export/export-2026-09-30.json', 'results/paper_export/latest.json',
    'results/_r509bmb_s0_integrate.py',
]
MERGED = ['CODELY.md', 'fleet/tasks/T-2026-10-01-141-P1.json', 'results/pool_core_samples.jsonl']

print("== gate 7b: ledger sanity + W10 completeness ==")
import science_gates as sg
head = sg.ledger_head()
print("   ledger_head:", head.get('total'), head.get('file'))
assert int(head['total']) == 382239, "ledger head must remain 382,239 (W9)"
n_w10 = run(['git', 'ls-files', 'results/p2cal_ext/n1_w10']).stdout.decode().strip().splitlines()
n_cl = [x for x in run(['git', 'ls-files', 'results/pool_claims']).stdout.decode().strip().splitlines()
        if 'PERPETUAL-N1-W10' in x]
print("   W10 products:", len(n_w10), "W10 claims:", len(n_cl))
assert len(n_w10) == 12 and len(n_cl) == 12

print("== step 8: commit integration ==")
run(['git', 'add', '-A', '--'] + RESTORE + MERGED)
r = run(['git', 'commit', '-m',
         "round 509 S0 integration: adopt r508 crashed-session residue onto origin/main "
         "(r314 CAS route, single carry commit) -- bm-b saturation engine instance "
         "(scripts/saturation_engine.py + s3 face wiring) + W10 first engine wave 12/12 "
         "products + pool claims provenance + engine telemetry + bm-b lane faces + "
         "CODELY/ticket/pool-samples union; shared derive faces take origin side "
         "[via bm-b]"], check=False)
if r.returncode != 0:
    print("COMMIT OUTPUT:", r.stdout.decode()[-800:], r.stderr.decode()[-800:]); sys.exit(3)
new_sha = run(['git', 'rev-parse', 'HEAD']).stdout.decode().strip()
print("   integration commit:", new_sha)

print("== step 9: CAS move main ref + checkout ==")
cas = run(['git', 'update-ref', 'refs/heads/main', new_sha, '5b8d72c45'], check=False)
if cas.returncode != 0:
    print("CAS FAILED:", cas.stderr.decode()[-400:]); sys.exit(4)
run(['git', 'checkout', 'main'])
print("   main now at:", run(['git', 'rev-parse', 'main']).stdout.decode().strip())
print("INTEGRATION OK")
